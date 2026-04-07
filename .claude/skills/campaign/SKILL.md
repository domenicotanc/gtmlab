---
name: campaign
description: Create an A/B experiment from existing prospect sequences. Groups prospects, assigns variants, and exports a CSV for Salesloft import. Use when the user wants to create a campaign, run an A/B test, or export sequences for sending.
allowed-tools: Read Write Bash Glob
---

# Create Campaign: $ARGUMENTS

Group prospects into an A/B experiment, randomly assign each to a variant, and export a CSV ready for Salesloft import.

**Expected arguments:** `{campaign-name} {prospect1} {prospect2} ...`
Example: `/campaign Q2-pain-vs-value stripe notion linear figma vercel`

## Process

### 1. Parse Arguments

The first argument is the campaign name (used as the experiment name). Remaining arguments are prospect slugs (lowercase company names matching `data/sequences/{slug}/`).

If no prospects are listed, scan `data/sequences/` and show available prospects.

### 2. Validate Sequences Exist

For each prospect, check that `data/sequences/{prospect-slug}/variant-a.json` and `variant-b.json` exist.

If any prospect is missing sequences:
```
Missing sequences for: {prospect}
Run /generate {prospect} first, then retry.
```

### 3. Determine Angles

Read the variant files from the first prospect to detect the angles (from the `angle` field in the JSON). These should be consistent across all prospects.

If angles differ across prospects (e.g., some were generated with custom angles), warn the user and use the angles from the first prospect as the experiment's official angles.

### 4. Create Experiment

Generate an experiment ID: `exp-` + 3-digit sequential number (check existing files in `data/experiments/` to determine the next number).

Save `data/experiments/{id}.json`:

```json
{
  "id": "exp-001",
  "name": "Q2-pain-vs-value",
  "angle_a": "pain-focused",
  "angle_b": "value-focused",
  "status": "draft",
  "assignments": {
    "stripe": "A",
    "notion": "B",
    "linear": "A",
    "figma": "B",
    "vercel": "A"
  },
  "prospects": ["stripe", "notion", "linear", "figma", "vercel"],
  "created_at": "ISO timestamp",
  "completed_at": null
}
```

### 5. Randomly Assign Variants

Randomly assign each prospect to variant A or B, aiming for a roughly even split. For odd numbers, one group will have one extra.

### 6. Export CSV

Create the export directory if needed: `data/exports/`

Build the CSV with one row per prospect, including only their assigned variant's emails. Use the flattened format:

```bash
python3 scripts/csv_export.py sequences data/sequences/{prospect-slug}/ -o data/exports/{experiment-id}-sequences.csv
```

Note: The standard export script exports both variants. For the campaign export, build a custom CSV that includes only the assigned variant per prospect. Construct this by:
1. Reading each prospect's assigned variant file
2. Building one row per prospect with the flattened columns
3. Writing directly to the output CSV

The CSV should have columns:
`experiment_id, variant, variant_angle, prospect_company, contact_name, prospect_email, subject_1, body_1, subject_2, body_2, subject_3, body_3, subject_4, body_4, subject_5, body_5`

### 7. Output

```
## Campaign: {name} (exp-{id})

**Angles:** A = {angle_a} | B = {angle_b}

### Assignment

| Prospect | Variant | Contact |
|----------|---------|---------|
| Stripe   | A       | sarah@stripe.com |
| Notion   | B       | alex@notion.so |
| Linear   | A       | james@linear.app |
| Figma    | B       | maria@figma.com |
| Vercel   | A       | lee@vercel.com |

**Split:** A = {count_a} | B = {count_b}

Exported to `data/exports/{id}-sequences.csv` ({total} rows)

### Next Steps
1. Create two Salesloft cadences: one for Variant A prospects, one for Variant B
2. Import the CSV rows into the matching cadence
3. Run the campaigns
4. When results come in: `/import-results {id} A cadence-a-export.csv B cadence-b-export.csv`
```

## Rules

- The random assignment must be deterministic per experiment — save it in the experiment JSON so it can be reproduced.
- If a prospect has no contact_email in their sequence data, include them but note the missing email.
- If only 1 prospect is provided, warn that A/B testing requires multiple prospects for meaningful results, but allow it (assign to A).
