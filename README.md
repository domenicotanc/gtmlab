# GTM Lab

> An AI-native experimentation toolkit for GTM teams. Research prospects, generate A/B email variants, prep SPICED discovery calls, and measure what actually works — all from your terminal.

## The Problem

GTM teams generate outreach content but rarely close the feedback loop. They don't know which angles, tones, or value props actually drive opens and replies. Without experimentation infrastructure, growth is guesswork.

Traditional tools make this worse: you need one tool to research, another to write, another to send, another to analyze. By the time you've context-switched through four UIs, the velocity needed for 2-4 experiments per week is impossible.

## What GTM Lab Does

GTM Lab is a set of Claude Code skills that turn your terminal into a GTM workstation. No web app, no API keys, no deployment. The AI agent is the interface.

1. **`/analyze stripe.com`** — Research a prospect's website and online presence. Produces a structured profile with pain points, competitive positioning, and fit assessment.

2. **`/generate stripe`** — Create a 5-email cold outreach sequence in two A/B variants. Angles are configurable (default: pain-focused vs value-focused).

3. **`/campaign Q2-test stripe notion linear`** — Group prospects into an experiment, randomly assign each to variant A or B, and export a CSV ready for Salesloft import.

4. **`/discover stripe`** — Prep for a discovery call with a Prospect Intelligence Brief and tailored SPICED framework questions grounded in real research.

5. **`/import-results exp-001 A cadence-a.csv B cadence-b.csv`** — Import Salesloft cadence results for both variants. Computes open rates, click rates, and statistical significance with z-tests.

6. **`/experiment exp-001`** — View the full experiment report: assignments, metrics comparison, significance badges, and winner declaration.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/gtmlab.git
cd gtmlab

# Open Claude Code
claude

# Set up your product context
/setup

# Start prospecting
/analyze stripe.com
/generate stripe
/discover stripe
```

That's it. No `npm install`, no environment variables, no build step.

## Experimentation Workflow

```
/analyze → /generate → /campaign → send via Salesloft → /import-results → /experiment
    ↑                                                                          |
    └──────────── iterate: champion vs challenger angles ←────────────────────┘
```

**Step by step:**
1. **Research** — `/analyze` one or more prospects, or `/bulk` a CSV
2. **Generate** — `/generate` creates two angle variants per prospect (both saved, nothing sent)
3. **Campaign** — `/campaign` groups prospects, assigns each to A or B, exports CSV for Salesloft
4. **Send** — Create two Salesloft cadences (one per variant), import the CSV rows
5. **Measure** — Export step results from each cadence, `/import-results` to analyze
6. **Iterate** — Winner becomes the champion, test a new challenger angle

## Architecture

- **Skills as product** — Each feature is a Claude Code skill file (`.claude/skills/`). The AI agent reads the skill, executes the workflow, and produces structured output. No application code to maintain.
- **Flat file data** — Prospects, experiments, and sequences are JSON/markdown files in `data/`. Git-tracked, portable, human-readable.
- **Python for reliability** — Statistical analysis and CSV parsing run as Python scripts called by the skills. The agent interprets; the scripts compute. No hallucinated p-values.
- **Zero dependencies** — No API keys, no databases, no frameworks. Just Claude Code and Python (stdlib only).

## Skills Reference

| Skill | Description |
|-------|-------------|
| `/setup` | Configure your product context |
| `/analyze {company or url}` | Research a prospect company |
| `/generate {company} [angle-a angle-b]` | Generate A/B email sequences (configurable angles) |
| `/discover {company}` | SPICED discovery call prep |
| `/bulk {csv-path}` | Generate sequences for multiple prospects from CSV |
| `/campaign {name} {prospect1} {prospect2} ...` | Create experiment, assign A/B split, export CSV |
| `/import-results {exp-id} A {csv-a} B {csv-b}` | Import Salesloft cadence results |
| `/experiment [exp-id]` | View experiment details or list all |
| `/export {sequences\|results} {exp-id}` | Export data as CSV |

## SPICED Framework

The `/discover` skill implements the Winning by Design SPICED methodology:

- **S**ituation — Background facts, qualify fit
- **P**ain — Challenges and frustrations (emotional + rational)
- **I**mpact — Business objectives the solution addresses
- **C**ritical **E**vent — Deadlines that drive decisions
- **D**ecision — Process, committee, criteria

Every question is grounded in actual research about the specific prospect. Generic questions are flagged as a red flag.

## Built With

Claude Code, Python 3, and the SPICED sales methodology by Winning by Design.
