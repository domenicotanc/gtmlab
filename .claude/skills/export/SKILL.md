---
name: export
description: Export sequences or experiment results as CSV. Use when the user wants to download, export, or save experiment data as CSV.
allowed-tools: Read Write Bash Glob
---

# Export Data: $ARGUMENTS

Export sequences or experiment results as CSV files.

**Expected arguments:** `{type} {experiment-id}`
- `/export sequences exp-001` — export email sequences with variant tags
- `/export results exp-001` — export experiment metrics

## Process

### Export Sequences

```bash
python3 scripts/csv_export.py sequences data/sequences/{experiment-id}/ -o data/exports/{experiment-id}-sequences.csv
```

Create the `data/exports/` directory if it doesn't exist.

Show the user:
```
Exported {n} rows to data/exports/{experiment-id}-sequences.csv

Format: One row per variant per prospect (ready for Salesloft/Outreach/Apollo import)
Columns: experiment_id, variant, variant_angle, prospect_company, contact_name, prospect_email, subject_1, body_1, subject_2, body_2, ..., subject_5, body_5
```

### Export Results

```bash
python3 scripts/csv_export.py results data/experiments/{experiment-id}-metrics.json -o data/exports/{experiment-id}-results.csv
```

Show the user:
```
Exported metrics to data/exports/{experiment-id}-results.csv

Columns: variant, total_sent, total_opened, total_replied, total_clicked, total_meetings, open_rate, reply_rate, click_rate, meeting_rate
```

### If no arguments or invalid type

Show usage:
```
Usage:
  /export sequences exp-001  — export email sequences as CSV
  /export results exp-001    — export experiment metrics as CSV

Available experiments:
{list experiment IDs from data/experiments/}
```

## Rules

- If the experiment or sequence files don't exist, say so clearly and suggest next steps.
- Always create the `data/exports/` directory before writing.
