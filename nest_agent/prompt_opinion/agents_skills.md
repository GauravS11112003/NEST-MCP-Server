# Prompt Opinion — coordinator agent skills

Use **Agents → BYO Agents → your agent → A2A & Skills**.

## ZIP layout (required by Prompt Opinion)

The archive must contain **exactly one** top-level folder, and **`SKILL.md` must live directly inside that folder** (not beside it at zip root, not only under deeper nested folders).

Correct:

```text
my-skill.zip
  my-skill/
    SKILL.md
```

Wrong:

```text
bad.zip
  SKILL.md                 ← at zip root

bad2.zip
  bundle/
    real-skill/
      SKILL.md             ← SKILL not directly under first directory
```

## Single zip (recommended upload)

**[`po_skill_packages/nest-coordinator-skills.zip`](po_skill_packages/nest-coordinator-skills.zip)**

Contains `nest-coordinator-skills/SKILL.md` — one merged document with **five** labeled surfaces (transition + FHIR + urgent triage + mood + SDOH).

Folder source: [`po_skill_packages/nest-coordinator-skills/`](po_skill_packages/nest-coordinator-skills/).

## Manual Name + Description

Use the YAML `name` / `description` in that `SKILL.md`, or register five separate UI skills using the per-skill folders under [`po_skill_packages/`](po_skill_packages/) and the text in each file’s frontmatter.

## Legacy

Optional copies under [`coordinator_skills/`](coordinator_skills/) are for reference only; **upload from `po_skill_packages/`** so paths stay valid.
