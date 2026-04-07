---
name: experiment
description: View experiment details, sequences, and A/B test results. Use when the user wants to see an experiment, check experiment status, list experiments, or view A/B test results.
allowed-tools: Read Bash Glob
---

# View Experiment: $ARGUMENTS

Display experiment details, campaign assignments, and performance metrics.

## Behavior

### If no argument is provided — list all experiments

Scan `data/experiments/` for all `exp-*.json` files (exclude `-results.json` and `-metrics.json`).

Display a summary table:

```
## All Experiments

| ID      | Name              | Status    | Created    | Winner |
|---------|-------------------|-----------|------------|--------|
| exp-001 | Q2-pain-vs-value  | completed | 2026-04-07 | B      |
| exp-002 | Q2-value-vs-story | draft     | 2026-04-07 | —      |

> View details: /experiment exp-001
> Import results: /import-results exp-001 A a.csv B b.csv
```

### If an experiment ID is provided — show full details

Read these files:
- `data/experiments/{id}.json` — metadata + assignments
- `data/experiments/{id}-metrics.json` — metrics (if exists)

For each prospect in the experiment's `assignments`, read their sequences from `data/sequences/{prospect-slug}/`.

Display the full experiment report:

```
## Experiment: {id} — {name}

**Angles:** A = {angle_a} | B = {angle_b}
**Status:** {status}
**Created:** {created_at}

---

### Campaign Assignment

| Prospect | Variant | Angle | Contact |
|----------|---------|-------|---------|
| Stripe   | A       | pain-focused | sarah@stripe.com |
| Notion   | B       | value-focused | alex@notion.so |
| Linear   | A       | pain-focused | james@linear.app |

**Split:** A = {count_a} | B = {count_b}
```

If metrics exist, append the results section:

```
---

### Results

**Total sent:** A = {a_sent} | B = {b_sent}
**Sample adequate:** {yes/no}

| Metric       | Variant A | Variant B | Diff    | Significance             |
|--------------|-----------|-----------|---------|--------------------------|
| Open Rate    | 33.3%     | 52.9%     | +19.6pp | Significant (p=0.012)    |
| Click Rate   | 5.8%      | 8.8%      | +3.0pp  | Not significant (p=0.42) |
| Bounce Rate  | 1.4%      | 0.0%      | -1.4pp  | Not significant (p=0.31) |

### Winner: {Variant B wins on open rate (p=0.012) / No winner yet — need more data}

### Confidence Intervals (95%)
- Open Rate: A [{lower}%, {upper}%] vs B [{lower}%, {upper}%]
```

If no metrics exist:
```
---

> No results imported yet.
> 1. Export: /export sequences {id}
> 2. Send via Salesloft (one cadence per variant)
> 3. Import: /import-results {id} A cadence-a.csv B cadence-b.csv
```

Optionally, if the user wants to see the actual email sequences, show them per prospect:

```
---

### Sequences: {prospect_name} (Variant {assigned_variant})

**Email 1 — Opener**
Subject: {subject}
{body}

(... all 5 emails ...)
```

## Rules

- Show the assignment table — this is the core of the experiment view.
- Format email bodies as readable text, not raw JSON.
- If files are missing (e.g., sequences not generated for a prospect), note what's missing rather than failing.
- Show sequences only if the user asks or if there are few prospects (< 5). For larger experiments, show assignments only.
