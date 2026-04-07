---
name: import-results
description: Import Salesloft cadence results and compute A/B test metrics with statistical significance. Use when the user wants to import campaign results, analyze A/B test performance, or check statistical significance.
allowed-tools: Read Write Bash Glob
---

# Import Campaign Results: $ARGUMENTS

Import Salesloft cadence step exports for both variants and compute A/B performance metrics with statistical significance.

**Expected arguments:** `{experiment-id} A {variant-a-csv} B {variant-b-csv}`
Example: `/import-results exp-001 A data/cadence-a-steps.csv B data/cadence-b-steps.csv`

## Process

### 1. Validate Experiment

Parse the experiment ID from the first argument. Read `data/experiments/{id}.json` to confirm it exists.

If the experiment doesn't exist, show available experiments:
```bash
ls data/experiments/exp-*.json 2>/dev/null | grep -v results | grep -v metrics
```

### 2. Parse Both CSVs

Parse each Salesloft cadence export using the salesloft mode:

```bash
python3 scripts/csv_parse.py salesloft "{variant-a-csv}" > /tmp/variant-a-parsed.json
python3 scripts/csv_parse.py salesloft "{variant-b-csv}" > /tmp/variant-b-parsed.json
```

Show the user what was detected for each:
```
Variant A CSV:
  Steps found: 4 (Email 1, Email 2, Email 3, Email 4)
  Total sent: 35 | Viewed: 14 | Clicked: 2 | Bounced: 1

Variant B CSV:
  Steps found: 4 (Email 1, Email 2, Email 3, Email 4)
  Total sent: 34 | Viewed: 18 | Clicked: 3 | Bounced: 0
```

### 3. Save Raw Results

Combine both parsed results into `data/experiments/{id}-results.json`:

```json
{
  "variant_a": { "label": "A", "rows": [...] },
  "variant_b": { "label": "B", "rows": [...] }
}
```

### 4. Compute Metrics

Run the stats script with the Salesloft analysis mode:

```bash
python3 scripts/stats.py analyze-salesloft A /tmp/variant-a-parsed.json B /tmp/variant-b-parsed.json
```

Save the output to `data/experiments/{id}-metrics.json`.

### 5. Update Experiment Status

Update `data/experiments/{id}.json`:
- Set `status` to `"completed"`
- Set `completed_at` to current ISO timestamp

### 6. Display Results

Format the metrics as a readable report:

```
## Experiment Results: {experiment name}

**Angles:** A = {angle_a} | B = {angle_b}
**Total sent:** A = {a_sent} | B = {b_sent}
**Sample adequate:** {yes/no}

### Metrics Comparison

| Metric       | Variant A | Variant B | Diff    | Significance             |
|--------------|-----------|-----------|---------|--------------------------|
| Open Rate    | 33.3%     | 52.9%     | +19.6pp | Significant (p=0.012)    |
| Click Rate   | 5.8%      | 8.8%      | +3.0pp  | Not significant (p=0.42) |
| Bounce Rate  | 1.4%      | 0.0%      | -1.4pp  | Not significant (p=0.31) |

Note: Reply rate not available in Salesloft step export.

### Winner
{If significant: "Variant B wins on open rate (p=X)"}
{If not significant: "No winner yet — need more data."}

### Confidence Intervals (95%)
- Open Rate: A [{lower}%, {upper}%] vs B [{lower}%, {upper}%]

> Results saved to data/experiments/{id}-results.json
> Metrics saved to data/experiments/{id}-metrics.json
> View full experiment: /experiment {id}
```

## Salesloft Column Mapping

| Salesloft Column | Maps To |
|-----------------|---------|
| Sent emails | sent |
| Viewed | opened |
| Clicked | clicked |
| Bounced | bounced |
| Name | step_name (Email 1, Email 2, etc.) |
| Day | day (cadence day number) |

**Not available in Salesloft step export:** replies, meetings booked. These metrics will show as 0.

## Rules

- Always show the significance label, not just the p-value.
- If sample size is below 30 per variant, warn that results may be unreliable.
- Primary winner metric is **open rate** (since Salesloft doesn't export replies).
- If only one CSV is provided, ask for the second variant's CSV.
- Steps with 0 sent (not yet executed) are included but don't affect rates.
