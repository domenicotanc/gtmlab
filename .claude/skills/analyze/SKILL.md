---
name: analyze
description: Analyze a prospect company's website and online presence. Use when the user wants to research a company, analyze a prospect, or prepare for outreach.
allowed-tools: WebFetch WebSearch Read Write Bash Glob
---

# Analyze Prospect: $ARGUMENTS

Research and analyze the prospect company to build a structured intelligence profile for outreach personalization.

## Process

### 1. Load Product Context

Read `data/context/product.json` to understand what the user's company does. All analysis should assess fit relative to this product.

If product context is empty or missing, warn the user to run `/setup` first, but continue with the analysis.

### 2. Check for Existing Data

Check if `data/prospects/` already contains a JSON file for this company (match by name, case-insensitive). If it exists, inform the user and ask if they want to refresh or use existing data.

### 3. Research the Company

Use **WebSearch** to find:
- What the company does (business model, products/services)
- Industry, market segment
- Company size / headcount estimates
- Funding history, stage, investors
- Recent news, product launches, leadership changes
- Technology stack signals (job postings, integrations page)
- Competitive positioning

Use **WebFetch** to scrape key pages from the company's website:
- Homepage — messaging, positioning, value props
- About page — mission, team size, locations
- Pricing page — business model, tiers, target customer
- Product/features page — what they actually sell
- Careers page — growth signals, team priorities

Limit to 3-5 pages. Focus on pages that reveal pain points and business context.

### 4. Produce Structured Analysis

Generate a JSON profile with this structure:

```json
{
  "company_name": "Acme Corp",
  "domain": "acme.com",
  "website_url": "https://acme.com",
  "industry": "Fintech",
  "company_size": "50-200",
  "funding_stage": "Series B",
  "description": "One-paragraph summary of what the company does",
  "products_services": ["Product A", "Product B"],
  "target_market": "Enterprise financial institutions",
  "competitive_positioning": "How they differentiate",
  "pain_points": [
    "Pain point relevant to our product"
  ],
  "recent_news": [
    "Notable recent development"
  ],
  "technology_signals": ["Tech stack hints"],
  "fit_assessment": "Strong|Moderate|Weak",
  "fit_reasoning": "Why this is/isn't a good fit for our product",
  "contact_name": "",
  "contact_title": "",
  "contact_email": "",
  "analyzed_at": "ISO timestamp"
}
```

### 5. Save Results

Save the JSON to `data/prospects/{company-name-slug}.json` (lowercase, hyphens for spaces).

### 6. Output Summary

Display a formatted summary to the user:

```
## {Company Name} — Prospect Analysis

**Industry:** {industry} | **Size:** {size} | **Fit:** {Strong/Moderate/Weak}

### What They Do
{description}

### Pain Points (relevant to our product)
1. {pain}
2. {pain}

### Recent Signals
- {news/development}

### Fit Assessment
{fit_reasoning}

> Saved to data/prospects/{slug}.json
> Next: /generate {company} or /discover {company}
```

## Rules

- Be specific. Generic analysis is useless — every finding should be grounded in actual research.
- Assess fit honestly. If the prospect isn't a good match, say so.
- If WebFetch fails on a URL, skip it and note what couldn't be accessed. Don't fabricate content.
- Keep pain points focused on what's relevant to the user's product context.
