---
name: setup
description: Configure GTM Lab with your product context. Use on first run or when the user wants to update their company/product information.
allowed-tools: WebFetch WebSearch Read Write Bash Glob
---

# GTM Lab Setup

Configure your product context so all prospect analysis, email generation, and discovery prep is grounded in your actual product.

## Process

### 1. Check Current State

Read `data/context/product.json`. If it already has content, show the current configuration and ask if the user wants to update it.

### 2. Gather Product Information

Ask the user for:

1. **Company name** — "What's your company called?"
2. **Product description** — "Describe your product in 2-3 sentences. What do you sell, who is it for, and what problem does it solve?"
3. **Website URL** (optional) — "What's your website? I can analyze it to enrich the product context."

### 3. Enrich from Website (if URL provided)

If a URL is provided:
- Use **WebFetch** to scrape the homepage, about page, and product/features page
- Use **WebSearch** to find additional context (press, reviews, competitors)
- Generate an enriched product context that supplements the user's description with:
  - Key features and capabilities
  - Target market and ideal customer profile
  - Competitive differentiation
  - Common use cases

### 4. Save Configuration

Write to `data/context/product.json`:

```json
{
  "company_name": "Acme Corp",
  "description": "User's original description",
  "source_url": "https://acme.com",
  "generated_context": "AI-enriched product context with features, market, differentiation...",
  "updated_at": "ISO timestamp"
}
```

### 5. Confirm Setup

```
## GTM Lab Configured

**Company:** {name}
**Website:** {url}
**Context:** {first 200 chars of generated_context}...

You're ready to go:
- /analyze {company} — research a prospect
- /generate {company} — create A/B email sequences
- /discover {company} — prep for a discovery call
- /bulk prospects.csv — process prospects in bulk
```

## Rules

- Don't overwrite existing context without asking.
- The generated context should be factual — sourced from the actual website content, not fabricated.
- If no URL is provided, that's fine — the user's description alone is sufficient.
