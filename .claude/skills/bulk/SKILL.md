---
name: bulk
description: Generate email sequences for multiple prospects from a CSV file. Use when the user wants to process a list of prospects in bulk.
allowed-tools: WebFetch WebSearch Read Write Bash Glob
---

# Bulk Generate Sequences: $ARGUMENTS

Parse a CSV file of prospects and generate A/B email sequences for each one.

**Note:** This creates sequences only — no experiments are created. Use `/campaign` afterwards to group prospects into an experiment and export for sending.

## Process

### 1. Parse the CSV

Run the CSV parser to normalize the prospect data:

```bash
python3 scripts/csv_parse.py prospects "$ARGUMENTS"
```

If parsing fails, show the error and suggest checking the file format.

Review the detected column mapping and row count. Show the user:
- How many rows were found
- Which columns were mapped
- Which columns couldn't be mapped

If `company_name` couldn't be detected, stop and ask the user which column contains company names.

### 2. Load Product Context

Read `data/context/product.json`. Warn if empty but continue.

### 3. Process Each Prospect

For each row in the CSV, sequentially:

**a. Research** — Using the company name (and domain/website_url if available):
- Use **WebSearch** for company context
- Use **WebFetch** on the company website if a URL is available (limit to 2 pages per prospect)
- Save prospect profile to `data/prospects/{company-slug}.json`

**b. Generate sequences** — Using the prospect profile:
- Generate a 5-email sequence in two variants (default: A = pain-focused, B = value-focused)
- Save sequences to `data/sequences/{prospect-slug}/variant-a.json` and `variant-b.json`

**c. Report progress** after each row:
```
[{current}/{total}] {company_name} — done
```

If a row fails, log the error and continue:
```
[{current}/{total}] {company_name} — SKIPPED: {reason}
```

### 4. Summary

```
## Bulk Generation Complete

**Processed:** {success}/{total} prospects
**Skipped:** {skipped}

| # | Company | Status |
|---|---------|--------|
| 1 | Stripe  | Done   |
| 2 | Notion  | Done   |
| 3 | Acme    | Skipped: no website found |

> Next: /campaign {name} stripe notion ... to create an experiment and export
```

## Rules

- Process sequentially. Show progress after each row.
- If a row has minimal data (just a company name), still attempt WebSearch.
- Don't stop the whole batch if one row fails — log and continue.
- Limit WebFetch to 2 pages per prospect to keep things moving.
