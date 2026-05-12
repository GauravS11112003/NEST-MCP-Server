"""
Clinical Knowledge MCP Server — reusable clinical reference tools.

Exposes 4 tools that any agent (or any MCP-capable client) can call:

  beers_criteria_lookup        — Is this med on the AGS Beers Criteria 2023?
  drug_interaction_check       — Check a list of meds for known DDIs.
  renal_dose_adjustment        — Recommended dose for a med at given eGFR.
  anticholinergic_burden       — Total ACB score across a med list.

This server is **stateless clinical knowledge**. It does not access patient
records and does not require FHIR credentials. Patient-specific reasoning
happens in the agent that calls these tools (e.g., SafeRx Council).

Run as HTTP (SSE transport) for Prompt Opinion registration:
    python -m clinical_knowledge_mcp.server --http --port 9001

Run as stdio (for local testing with mcp inspector):
    python -m clinical_knowledge_mcp.server
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .data import (
    calculate_total_acb,
    get_renal_recommendation,
    lookup_beers,
)
from .fhir_context import (
    get_fhir_context,
    latest_egfr,
    list_active_medications,
    patient_age_years,
)
from .rxnav_client import check_all_pairs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("clinical_knowledge_mcp")


# ── MCP server ─────────────────────────────────────────────────────────────────

server: Server = Server("clinical-knowledge-mcp")


# Prompt Opinion's FHIR-context extension. Declared in the initialize response
# so PO knows this server can accept patient context. Scopes are advertised as
# requested permissions; the user grants them in the PO settings UI.
# Docs: https://docs.promptopinion.ai/fhir-context/mcp-fhir-context
_FHIR_EXTENSION_KEY = "ai.promptopinion/fhir-context"
_FHIR_EXTENSION_VALUE: dict[str, Any] = {
    "scopes": [
        {"name": "patient/Patient.rs"},
        {"name": "patient/MedicationRequest.rs"},
        {"name": "patient/Observation.rs"},
        {"name": "patient/Condition.rs"},
    ],
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="beers_criteria_lookup",
            description=(
                "Check whether a single medication appears on the AGS Beers Criteria 2023 "
                "list of potentially inappropriate medications for older adults (≥65 yr). "
                "Returns the Beers category, rationale, recommendation, severity, and "
                "evidence/recommendation strength. "
                "Use this whenever an agent is reviewing the medication list of an older patient."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "medication": {
                        "type": "string",
                        "description": "Generic medication name (case-insensitive). E.g., 'diphenhydramine', 'oxybutynin'.",
                    }
                },
                "required": ["medication"],
            },
        ),
        Tool(
            name="drug_interaction_check",
            description=(
                "Given a list of medications, return all known clinically significant "
                "drug-drug interactions. Each interaction includes severity (HIGH/MODERATE/LOW), "
                "mechanism, and clinical recommendation. "
                "Sources: curated high-yield DDI table derived from ASHP, FDA labeling, and "
                "DrugBank patterns. Use this to perform polypharmacy safety review."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "medications": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of generic medication names.",
                    }
                },
                "required": ["medications"],
            },
        ),
        Tool(
            name="renal_dose_adjustment",
            description=(
                "Return the recommended dose adjustment for a medication at a given "
                "eGFR (ml/min/1.73m^2). Reports the CKD stage and a specific "
                "recommendation drawn from package inserts and KDIGO guidelines. "
                "Critical for safe prescribing in older adults and CKD patients."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "medication": {
                        "type": "string",
                        "description": "Generic medication name.",
                    },
                    "egfr": {
                        "type": "number",
                        "description": "Estimated GFR in ml/min/1.73m^2 (e.g., 38).",
                    },
                },
                "required": ["medication", "egfr"],
            },
        ),
        Tool(
            name="anticholinergic_burden",
            description=(
                "Calculate the cumulative Anticholinergic Cognitive Burden (ACB) score "
                "for a list of medications. Each contributing drug is scored 1-3 per the "
                "validated ACB scale. Total ACB ≥3 is clinically significant and is "
                "associated with increased cognitive impairment, falls, and mortality "
                "in older adults. Returns total score, risk level, contributors, and "
                "deprescribing recommendation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "medications": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of generic medication names.",
                    }
                },
                "required": ["medications"],
            },
        ),
        Tool(
            name="comprehensive_polypharmacy_review",
            description=(
                "[PATIENT-AWARE] Pull the active medication list and most recent eGFR "
                "directly from the patient's FHIR record, then run all four safety checks "
                "(Beers Criteria, drug-drug interactions, anticholinergic burden, renal "
                "dose adjustments) in a single call. Returns a unified report. "
                "Requires PromptOpinion FHIR context (patient/Patient.rs, "
                "patient/MedicationRequest.rs, patient/Observation.rs). "
                "Use this for one-shot polypharmacy reviews when the agent has FHIR "
                "context available."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info("tool_call name=%s args=%s", name, arguments)

    if name == "beers_criteria_lookup":
        result = _tool_beers_lookup(arguments.get("medication", ""))
    elif name == "drug_interaction_check":
        result = _tool_interactions(arguments.get("medications", []))
    elif name == "renal_dose_adjustment":
        result = _tool_renal(
            arguments.get("medication", ""),
            float(arguments.get("egfr", 0)),
        )
    elif name == "anticholinergic_burden":
        result = _tool_acb(arguments.get("medications", []))
    elif name == "comprehensive_polypharmacy_review":
        result = _tool_comprehensive_review()
    else:
        result = {"status": "error", "error_message": f"Unknown tool '{name}'"}

    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ── Tool implementations ───────────────────────────────────────────────────────

def _tool_beers_lookup(medication: str) -> dict[str, Any]:
    if not medication:
        return {"status": "error", "error_message": "medication is required"}
    entry = lookup_beers(medication)
    if entry is None:
        return {
            "status": "not_found",
            "medication": medication,
            "message": f"'{medication}' is not on our curated Beers Criteria 2023 subset.",
            "note": "Absence does not guarantee safety — consult full criteria for less common drugs.",
        }
    return {
        "status": "found",
        "medication": medication,
        **entry,
    }


def _tool_interactions(medications: list[str]) -> dict[str, Any]:
    if not medications:
        return {"status": "error", "error_message": "medications list is required"}
    if len(medications) < 2:
        return {
            "status": "success",
            "medication_count": len(medications),
            "interactions": [],
            "summary": "Only one medication provided; no pairs to check.",
        }

    interactions = check_all_pairs(medications)
    high_count = sum(1 for i in interactions if i.get("severity") == "HIGH")
    mod_count = sum(1 for i in interactions if i.get("severity") == "MODERATE")

    return {
        "status": "success",
        "medication_count": len(medications),
        "interactions_found": len(interactions),
        "summary": (
            f"Found {len(interactions)} interactions across {len(medications)} medications "
            f"({high_count} HIGH, {mod_count} MODERATE)."
        ),
        "high_severity_count": high_count,
        "moderate_severity_count": mod_count,
        "interactions": interactions,
    }


def _tool_renal(medication: str, egfr: float) -> dict[str, Any]:
    if not medication:
        return {"status": "error", "error_message": "medication is required"}
    if not egfr or egfr <= 0:
        return {"status": "error", "error_message": "valid eGFR (>0) is required"}
    rec = get_renal_recommendation(medication, egfr)
    return {"status": "success", **rec}


def _tool_acb(medications: list[str]) -> dict[str, Any]:
    if not medications:
        return {"status": "error", "error_message": "medications list is required"}
    return {"status": "success", "medication_count": len(medications), **calculate_total_acb(medications)}


def _tool_comprehensive_review() -> dict[str, Any]:
    """Pull patient meds + eGFR from FHIR, run all 4 safety checks at once."""
    ctx = get_fhir_context()
    if ctx is None:
        return {
            "status": "error",
            "error_message": (
                "FHIR context is not available. The user must authorize FHIR access "
                "for the Clinical Knowledge MCP server in PromptOpinion settings, and "
                "an active patient must be selected."
            ),
        }

    try:
        meds = list_active_medications()
    except Exception as e:
        logger.exception("comprehensive_review_meds_failed")
        return {
            "status": "error",
            "error_message": f"Could not load patient medications from FHIR: {e}",
        }

    if not meds:
        return {
            "status": "success",
            "patient_id": ctx.patient_id,
            "medication_count": 0,
            "summary": "Patient has no active MedicationRequests on file. No polypharmacy review needed.",
        }

    egfr = latest_egfr()
    age = patient_age_years()

    # 1. Beers screen
    beers_hits: list[dict[str, Any]] = []
    for med in meds:
        entry = lookup_beers(med)
        if entry:
            beers_hits.append({"medication": med, **entry})

    # 2. Interactions
    interactions = check_all_pairs(meds)

    # 3. Anticholinergic burden
    acb = calculate_total_acb(meds)

    # 4. Renal adjustments — only if we have an eGFR
    renal_findings: list[dict[str, Any]] = []
    if egfr is not None:
        for med in meds:
            rec = get_renal_recommendation(med, egfr)
            if rec.get("found"):
                renal_findings.append(rec)

    high_severity_count = (
        sum(1 for h in beers_hits if h.get("severity") == "HIGH")
        + sum(1 for i in interactions if i.get("severity") == "HIGH")
        + (1 if acb["total_score"] >= 6 else 0)
    )

    return {
        "status": "success",
        "patient_id": ctx.patient_id,
        "patient_age": age,
        "medication_count": len(meds),
        "egfr": egfr,
        "ckd_stage": (renal_findings[0].get("ckd_stage") if renal_findings else None),
        "high_severity_finding_count": high_severity_count,
        "summary": (
            f"Reviewed {len(meds)} active medications. "
            f"Found {len(beers_hits)} Beers Criteria concerns, "
            f"{len(interactions)} drug-drug interactions "
            f"({sum(1 for i in interactions if i.get('severity') == 'HIGH')} HIGH severity), "
            f"ACB score {acb['total_score']} ({acb['risk_level']}), "
            f"{len(renal_findings)} medications requiring renal review at eGFR={egfr}."
            if egfr is not None else
            f"Reviewed {len(meds)} active medications. eGFR not on file — renal review skipped. "
            f"Found {len(beers_hits)} Beers Criteria concerns, "
            f"{len(interactions)} drug-drug interactions, "
            f"ACB score {acb['total_score']} ({acb['risk_level']})."
        ),
        "active_medications": meds,
        "beers_criteria_findings": beers_hits,
        "drug_drug_interactions": interactions,
        "anticholinergic_burden": acb,
        "renal_dose_findings": renal_findings,
    }


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Clinical Knowledge MCP server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run as HTTP (SSE transport) instead of stdio. Required for Prompt Opinion.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9001,
        help="Port for HTTP transport (default 9001).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for HTTP transport (default 0.0.0.0).",
    )
    args = parser.parse_args()

    if args.http:
        run_http(args.host, args.port)
    else:
        run_stdio()


def _augment_with_fhir_extension(init_options):
    """Attach PromptOpinion's FHIR extension to a freshly-built InitializationOptions.

    `ServerCapabilities` is a Pydantic model with `extra='allow'`, so we can
    set the `extensions` attribute and Pydantic will serialize it into the
    `initialize` response exactly the way PromptOpinion expects.
    """
    caps = init_options.capabilities
    existing = getattr(caps, "extensions", None) or {}
    existing[_FHIR_EXTENSION_KEY] = _FHIR_EXTENSION_VALUE
    setattr(caps, "extensions", existing)
    if hasattr(caps, "model_extra") and isinstance(caps.model_extra, dict):
        caps.model_extra["extensions"] = existing
    return init_options


def _build_initialization_options():
    """Wrapper used by stdio transport."""
    return _augment_with_fhir_extension(server.create_initialization_options())


# Patch the server so transports that build InitializationOptions internally
# (StreamableHTTPSessionManager) automatically pick up the FHIR extension.
_original_create_init_options = server.create_initialization_options


def _patched_create_init_options(*args, **kwargs):
    return _augment_with_fhir_extension(_original_create_init_options(*args, **kwargs))


server.create_initialization_options = _patched_create_init_options  # type: ignore[method-assign]


def run_stdio() -> None:
    """Run over stdio (for local testing or in-process MCP clients)."""
    import asyncio

    async def _serve() -> None:
        async with stdio_server() as (read, write):
            await server.run(read, write, _build_initialization_options())

    logger.info("clinical-knowledge-mcp starting on stdio")
    asyncio.run(_serve())


def run_http(host: str, port: int) -> None:
    """Run over HTTP exposing BOTH Streamable-HTTP (modern) and SSE (legacy).

    Endpoints:
      POST/GET /mcp        → Streamable-HTTP transport (preferred by current
                             MCP clients such as Prompt Opinion's Inspector)
      GET      /sse        → Legacy SSE transport (left in place for older
                             clients that still depend on the old handshake)
      POST     /messages/  → Companion POST endpoint for the legacy SSE path

    Health endpoint:
      GET      /healthz    → Simple JSON `{"status":"ok"}` so a browser test
                             of the URL doesn't get a confusing 404.
    """
    import contextlib

    import uvicorn
    from mcp.server.sse import SseServerTransport
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    from .fhir_context import FhirHeaderMiddleware

    init_options = _build_initialization_options()

    # ── Streamable-HTTP transport (modern) ───────────────────────────────────
    streamable_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=False,
        stateless=False,
    )

    async def handle_streamable_http(scope, receive, send):
        await streamable_manager.handle_request(scope, receive, send)

    # ── SSE transport (legacy) ───────────────────────────────────────────────
    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse_transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(streams[0], streams[1], init_options)

    # ── Health & metadata ────────────────────────────────────────────────────
    async def handle_healthz(_request):
        return JSONResponse(
            {
                "status": "ok",
                "name": "clinical-knowledge-mcp",
                "transports": {
                    "streamable_http": "/mcp",
                    "sse": "/sse",
                },
                "tools": [
                    "beers_criteria_lookup",
                    "drug_interaction_check",
                    "renal_dose_adjustment",
                    "anticholinergic_burden",
                    "comprehensive_polypharmacy_review",
                ],
                "fhir_extension": _FHIR_EXTENSION_KEY,
                "fhir_scopes": _FHIR_EXTENSION_VALUE["scopes"],
            }
        )

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        async with streamable_manager.run():
            yield

    app = Starlette(
        debug=False,
        routes=[
            Route("/", endpoint=handle_healthz),
            Route("/healthz", endpoint=handle_healthz),
            Mount("/mcp", app=handle_streamable_http),
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse_transport.handle_post_message),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["mcp-session-id"],
            ),
        ],
        lifespan=lifespan,
    )

    # Starlette's Mount("/mcp", ...) redirects bare POST /mcp → POST /mcp/
    # via 307. Most MCP clients don't follow POST redirects, so we wrap the
    # whole app and rewrite `/mcp` → `/mcp/` *before* routing. This makes
    # both `POST /mcp` and `POST /mcp/` reach the Streamable-HTTP handler.
    inner_app = app

    async def _normalize_mcp_slash(scope, receive, send):
        if scope.get("type") == "http" and scope.get("path") == "/mcp":
            scope = dict(scope)
            scope["path"] = "/mcp/"
            scope["raw_path"] = b"/mcp/"
        await inner_app(scope, receive, send)

    # Wrap the whole app with the FHIR header middleware so each tool call
    # sees the active patient context via `get_fhir_context()`.
    app = FhirHeaderMiddleware(_normalize_mcp_slash)  # type: ignore[assignment]

    logger.info(
        "clinical-knowledge-mcp starting on http://%s:%d  endpoints: /mcp (preferred) /sse (legacy)",
        host,
        port,
    )
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("clinical-knowledge-mcp shutting down")
        sys.exit(0)
