---
name: discover
description: Generate a Prospect Intelligence Brief and SPICED discovery call questions for a company. Use when the user wants to prepare for a discovery call, generate SPICED questions, or research a prospect for a sales meeting.
allowed-tools: WebFetch WebSearch Read Write Bash Glob
---

# SPICED Discovery Prep: $ARGUMENTS

Generate a Prospect Intelligence Brief and tailored SPICED discovery questions.

## Coaching Guardrail — Validate Input First

If the company name is too vague or generic to research (e.g., "tech company", "startup", "that SaaS company"), **push back immediately**:

> "I need a specific company name to generate useful discovery questions. Generic questions are a red flag — every question must be grounded in real research about this specific prospect."

## Process

### 1. Load Product Knowledge

Read `data/context/product.json` to ground all output in actual product capabilities.

If empty, warn the user to run `/setup` first. All SPICED questions and the intelligence brief must connect back to real product capabilities. Do not fabricate features or value props.

### 2. Check Existing Prospect Data

Check `data/prospects/` for an existing profile of this company. If found, load it as a starting point — use the analysis to make questions more specific and avoid asking things we already know.

Also check `data/sequences/` for any prior experiments with this prospect.

### 3. Research the Company

Use **WebSearch** to gather current intelligence:

- Business model and core products/services
- Industry and regulated industry signals
- Funding history and stage
- Approximate headcount and growth trajectory
- Recent news, press releases, leadership changes
- Challenges relevant to our product

Use **WebFetch** on 2-3 key pages from their website if needed for deeper context.

If existing prospect data was found in step 2, focus research on **what's changed since the last analysis** — recent news, new developments, updated positioning.

### 4. Apply SPICED Framework

Apply the SPICED methodology:

Key framework principles:
- Prescription before diagnosis is malpractice — never pitch before understanding the problem
- Summarize what you've heard before moving forward (active listening)
- Share relevant customer stories that match the prospect's situation and pain
- Focus on Impact — it's the core of SPICED
- ICE is not always chronological — listen for clues about Impact and Critical Events early

### 5. Generate Prospect Intelligence Brief

Produce a structured brief:

| Section | Content |
|---------|---------|
| **Company Snapshot** | What the company does, size, industry, HQ, key products |
| **Strategic Context** | Market position, recent moves, competitive landscape, growth trajectory |
| **Product Fit Assessment** | **Strong** / **Moderate** / **Weak** — with reasoning tied to our product capabilities |
| **Likely Pain Areas** | 2-4 specific pains grounded in research, mapped to our product capabilities |
| **Potential Critical Events** | Upcoming deadlines, regulatory changes, growth milestones, board reviews that could drive urgency |
| **Stakeholder Notes** | Key personas likely involved in the decision, their probable priorities |
| **Open Questions** | 2-3 things we couldn't determine from research that discovery should uncover |

### 6. Generate SPICED Discovery Questions

Generate tailored, open-ended questions for each SPICED element:

| Element | Count | Guidance |
|---------|-------|---------|
| **Situation** | 3-4 | Show you've done research. Confirm facts, qualify fit. "I noticed X — did I get that right?" |
| **Pain** | 3-4 | Reference specific challenges from research. "When speaking to other [titles] in [industry], they mention X. To what extent is that a priority for you?" |
| **Impact** | 3-4 | Quantify business impact. "How does [pain] affect your ability to [business objective]?" |
| **Critical Event** | 3-4 | Surface deadlines, urgency, and what success looks like. "When do you need this in place?" → "What happens if you miss that date?" → "What would solving this unlock for your team?" |
| **Decision** | 2-3 | Map the buying process. "Have you brought in a platform like this before? How does your evaluation process work?" |

**Question rules:**
- Every question must be **open-ended** (no yes/no)
- Every question must be **grounded in research** — reference specific findings about this company
- Tone must be **conversational**, not interrogative
- Questions should **surface pain that our product can solve**
- Include a suggested **customer story prompt** after Pain questions
- If a question could apply to any company, it's not good enough — rewrite it

### 7. Save and Display

Save the full output to `data/prospects/{company-slug}-discovery.md`.

Display using this format:

```
## Prospect Intelligence Brief: {Company Name}

### Company Snapshot
{What they do, size, industry, HQ, key products}

### Strategic Context
{Market position, recent moves, competitive landscape}

### Product Fit Assessment: [Strong/Moderate/Weak]
{Reasoning tied to our product capabilities}

### Likely Pain Areas
1. {Specific pain → our product capability}
2. {Specific pain → our product capability}

### Potential Critical Events
- {Event with timing if known}

### Stakeholder Notes
- {Persona: likely priorities}

### Open Questions
- {What discovery should uncover}

---

## SPICED Discovery Questions

### Situation (3-4 questions)
1. ...

### Pain (3-4 questions)
1. ...

> Customer story prompt: "When we worked with [similar company in their industry], they were dealing with [similar pain]. What they found was..."

### Impact (3-4 questions)
1. ...

### Critical Event (3-4 questions)
1. ...

### Decision (2-3 questions)
1. ...

---

> Saved to data/prospects/{slug}-discovery.md
```

## Guardrails

- **No fabrication**: If web search returns limited results, say so in the brief. Don't invent company details.
- **Product grounding**: Every pain area and question must connect to a real product capability from `product.json`. If the fit is weak, say so honestly.
- **Quality over quantity**: Fewer sharp, specific questions beat many generic ones.
- **Honest assessment**: Report fit assessment honestly — Strong, Moderate, or Weak.
