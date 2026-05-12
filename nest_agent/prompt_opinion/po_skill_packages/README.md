# Prompt Opinion skill packages

Prompt Opinion expects **`SKILL.md` nested under the first (and only) top-level directory** in the zip—never a bare `SKILL.md` at the archive root, and not `outer/other-skill/SKILL.md` unless `outer` is the sole skill folder.

Correct layout:

```text
<skill-folder-name>.zip
  <skill-folder-name>/
    SKILL.md
```

## Single zip (all surfaces in one `SKILL.md`)

**[`nest-coordinator-skills.zip`](nest-coordinator-skills.zip)** contains exactly:

```text
nest-coordinator-skills/
  SKILL.md
```

Source folder: [`nest-coordinator-skills/`](nest-coordinator-skills/).

Regenerate:

```bash
cd nest_agent/prompt_opinion/po_skill_packages
rm -f nest-coordinator-skills.zip
zip -r nest-coordinator-skills.zip nest-coordinator-skills -x "*.DS_Store"
```

## One zip per skill (optional)

Each file has the same strict shape (`<name>/SKILL.md`):

| Zip |
| --- |
| `postpartum-dyad-transition-coordinator.zip` |
| `fhir-dyad-multipatient-context.zip` |
| `urgent-postpartum-neonatal-triage.zip` |
| `perinatal-mood-screen-safety-triage.zip` |
| `sdoh-access-discharge-barriers.zip` |

Regenerate (from `po_skill_packages`):

```bash
for d in postpartum-dyad-transition-coordinator fhir-dyad-multipatient-context \
         urgent-postpartum-neonatal-triage perinatal-mood-screen-safety-triage \
         sdoh-access-discharge-barriers; do
  rm -f "$d.zip"
  zip -r "$d.zip" "$d" -x "*.DS_Store"
done
```

**Do not** build per-skill archives with `cd "$d" && zip -r ../out.zip .` — that puts `SKILL.md` at the zip root and triggers PO’s validation error.
