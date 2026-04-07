# GTM Lab

AI-native GTM experimentation toolkit built as Claude Code skills.

## What This Is

A set of Claude Code skills for prospect analysis, A/B email generation, SPICED discovery prep, and experiment tracking. No web UI, no database, no deployment. Data persists as flat files (JSON/markdown).

## Project Structure

```
.claude/skills/     — Claude Code skill files (the product)
scripts/            — Python scripts for stats + CSV (reliable computation)
data/
  context/          — Product context (product.json)
  prospects/        — Prospect profiles ({company}.json)
  experiments/      — Experiment metadata, results, metrics
  sequences/        — Email sequences per prospect ({prospect-slug}/)
  exports/          — Generated CSV exports
  sample/           — Demo CSV files
docs/
  knowledge/        — SPICED framework PDFs (Winning by Design)
  spiced.md         — SPICED command reference
```

## Skills

| Skill | Purpose |
|-------|---------|
| `/setup` | Configure product context |
| `/analyze {company}` | Research a prospect |
| `/generate {company} [angle-a angle-b]` | Generate A/B email sequences |
| `/discover {company}` | SPICED discovery call prep |
| `/bulk {csv-path}` | Generate sequences for multiple prospects |
| `/campaign {name} {prospects...}` | Create experiment, assign A/B split, export CSV |
| `/import-results {id} A {csv} B {csv}` | Import Salesloft cadence results |
| `/experiment {id}` | View experiment + metrics |
| `/export {type} {id}` | Export as CSV |

## Key Workflow

Generation and experimentation are separate:
- `/generate` creates sequences per prospect (saved under `data/sequences/{prospect-slug}/`)
- `/campaign` groups prospects into an experiment, assigns variants, exports CSV
- `/import-results` imports Salesloft step exports (one CSV per variant/cadence)

## Data Conventions

- Prospect files: `data/prospects/{company-slug}.json` (lowercase, hyphens)
- Sequence dirs: `data/sequences/{prospect-slug}/` with `variant-a.json`, `variant-b.json`
- Experiment IDs: `exp-001`, `exp-002`, etc. (sequential)
- Experiment files: `data/experiments/{id}.json` (metadata + assignments)
- Results: `data/experiments/{id}-results.json`, metrics: `{id}-metrics.json`

## Python Scripts

All scripts accept CLI args and output JSON. No external dependencies (stdlib only).

- `scripts/stats.py` — z-test, confidence intervals, experiment analysis, Salesloft analysis
- `scripts/csv_parse.py` — CSV parsing with auto-detect column mapping (prospects, results, salesloft modes)
- `scripts/csv_export.py` — Export sequences (flattened: one row per variant per prospect) or results as CSV

## Salesloft Integration

- Export from `/campaign` produces CSV with flattened email columns (subject_1, body_1, ... subject_5, body_5)
- Import via `/import-results` expects Salesloft cadence step exports (Name, Day, Type, Bounced, Clicked, Sent emails, Viewed, etc.)
- Two CSVs imported per experiment (one per cadence/variant)
