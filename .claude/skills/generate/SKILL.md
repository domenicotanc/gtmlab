---
name: generate
description: Generate A/B cold email sequences for a prospect. Use when the user wants to create outreach emails, email campaigns, or cold email variants.
allowed-tools: WebSearch Read Write Bash Glob
---

# Generate Email Sequences: $ARGUMENTS

Generate a 5-email cold outreach sequence in two angle variants for the specified prospect.

**Note:** This creates sequences only — no experiment is created. Use `/campaign` to group prospects into an experiment when you're ready to send.

## Process

### 1. Load Context

**Product context:** Read `data/context/product.json`. If empty, warn the user to run `/setup` first.

**Prospect data:** Look for `data/prospects/{company-slug}.json` (lowercase, hyphens for spaces). If not found, ask the user to run `/analyze {company}` first or provide basic details (company name, what they do, contact name/title).

### 2. Determine Angles

Check if the user specified custom angles in the arguments (e.g., `/generate stripe value-focused story-driven`).

- If two angles provided: use those
- If no angles provided: default to **pain-focused** (A) and **value-focused** (B)

### 3. Generate Two Variants

Generate a 5-email sequence in **two variants**:

**Variant A — {angle_a}:** The first angle. Tailor subject lines, tone, and framing to this approach.

**Variant B — {angle_b}:** The second angle. Meaningfully different from A — not just word swaps.

Common angle examples:
- **Pain-focused** — lead with the prospect's likely challenges, agitate before solving
- **Value-focused** — lead with industry insights and education, share value before connecting to product
- **Story-driven** — lead with narrative, customer stories, and relatable scenarios
- **Direct-ask** — short, direct, get to the point fast
- **Educational** — teach something useful, position as thought leader

**Email sequence structure (same for both variants):**

| # | Type | Purpose |
|---|------|---------|
| 1 | Opener | Icebreaker + light intro, personalized to prospect |
| 2 | Value | Context + insight relevant to their industry/role |
| 3 | Social Proof | Case example or story of similar company |
| 4 | Follow-up | Urgency + useful resource |
| 5 | Breakup | Final touch, leave the door open |

**Email rules:**
- Subject lines: 1-4 words, adjusted to match each variant's angle
- Body: 100 words max, Grade 6 readability, conversational
- Personalize using prospect data (company name, industry, pain points, contact name/title)
- Reference specific findings from the prospect analysis — never be generic
- No placeholder text like [Company Name] — use actual values

### 4. Save Sequences

Save each variant to `data/sequences/{prospect-slug}/`:

**variant-a.json:**
```json
{
  "variant": "A",
  "angle": "pain-focused",
  "prospect": {
    "company_name": "Acme Corp",
    "contact_name": "Sarah Chen",
    "contact_email": "sarah@acme.com"
  },
  "emails": [
    {
      "number": 1,
      "type": "opener",
      "subject": "Quick question",
      "body": "Hi Sarah, ..."
    }
  ]
}
```

Create the directory `data/sequences/{prospect-slug}/` if it doesn't exist. If sequences already exist for this prospect, overwrite them (the user is regenerating).

### 5. Output Preview

Display both variants:

```
## Sequences: {Company Name}
Angles: A = {angle_a} | B = {angle_b}

### Variant A: {angle_a}
**Email 1 — Opener**
Subject: {subject}
{body}

**Email 2 — Value**
...

(all 5 emails)

---

### Variant B: {angle_b}
**Email 1 — Opener**
Subject: {subject}
{body}

**Email 2 — Value**
...

(all 5 emails)

---

> Sequences saved to data/sequences/{prospect-slug}/
> Next: /campaign {name} {prospect} to create an experiment and export
```

## Rules

- Every email must reference something specific from the prospect analysis. If the prospect file is thin, do additional WebSearch to enrich.
- Subject lines between variants must be meaningfully different — not just word swaps.
- Social proof emails (email 3) should reference realistic but clearly hypothetical examples. Don't claim real case studies that don't exist.
