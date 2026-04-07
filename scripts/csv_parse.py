#!/usr/bin/env python3
"""
CSV parser with auto-detect column mapping.

Parses CSV files (RFC 4180), auto-detects column mappings using regex
aliases, and outputs normalized JSON. Handles both prospect CSVs and
campaign results CSVs.

Usage:
  # Parse prospects CSV with auto-detect
  python3 scripts/csv_parse.py prospects data/sample/sample-prospects.csv

  # Parse Salesloft cadence step export
  python3 scripts/csv_parse.py salesloft data/sample/sample-results.csv

  # Parse generic results CSV with auto-detect
  python3 scripts/csv_parse.py results data/sample/sample-results.csv

  # Just show detected mapping without parsing
  python3 scripts/csv_parse.py detect data/some-file.csv
"""

import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Field aliases — regex patterns that match common CSV column names
# ---------------------------------------------------------------------------

PROSPECT_ALIASES = {
    "company_name": [
        r"company[\s_-]*name", r"^company$", r"organization",
        r"account[\s_-]*name", r"^account$", r"^name$",
    ],
    "domain": [
        r"^domain$", r"website[\s_-]*domain", r"company[\s_-]*domain",
        r"^url$", r"^site$",
    ],
    "website_url": [
        r"website[\s_-]*url", r"^website$", r"company[\s_-]*website",
        r"company[\s_-]*url", r"web[\s_-]*address", r"homepage",
    ],
    "industry": [
        r"^industry$", r"sector", r"vertical", r"market[\s_-]*segment",
    ],
    "company_size": [
        r"company[\s_-]*size", r"^size$", r"employees",
        r"employee[\s_-]*count", r"headcount", r"num[\s_-]*employees",
        r"team[\s_-]*size", r"^hc$",
    ],
    "contact_name": [
        r"contact[\s_-]*name", r"^contact$", r"full[\s_-]*name",
        r"^name$", r"person[\s_-]*name", r"lead[\s_-]*name",
        r"first[\s_-]*name",  # partial match, better than nothing
    ],
    "contact_title": [
        r"contact[\s_-]*title", r"^title$", r"job[\s_-]*title",
        r"^role$", r"^position$", r"designation",
    ],
    "contact_email": [
        r"contact[\s_-]*email", r"^email$", r"email[\s_-]*address",
        r"^e-mail$", r"work[\s_-]*email",
    ],
    "notes": [
        r"^notes?$", r"^comments?$", r"^description$", r"^memo$",
    ],
    "company_linkedin_url": [
        r"company[\s_-]*linkedin", r"linkedin[\s_-]*company",
        r"org[\s_-]*linkedin",
    ],
    "contact_linkedin_url": [
        r"contact[\s_-]*linkedin", r"linkedin[\s_-]*url",
        r"linkedin[\s_-]*profile", r"^linkedin$", r"person[\s_-]*linkedin",
    ],
}

RESULTS_ALIASES = {
    "variant": [
        r"^variant$", r"^version$", r"^group$", r"^cohort$",
        r"test[\s_-]*group", r"^ab[\s_-]*group$", r"^segment$",
    ],
    "email_number": [
        r"email[\s_-]*num", r"^step$", r"sequence[\s_-]*num",
        r"email[\s_-]*#", r"^email[\s_-]*step$", r"^number$",
        r"^seq$", r"^position$",
    ],
    "sent": [
        r"^sent$", r"^delivered$", r"^sends$", r"^deliveries$",
        r"total[\s_-]*sent",
    ],
    "opened": [
        r"^opened?$", r"^opens?$", r"open[\s_-]*count",
        r"unique[\s_-]*opens?", r"total[\s_-]*opens?",
    ],
    "clicked": [
        r"^clicked?$", r"^clicks?$", r"click[\s_-]*count",
        r"unique[\s_-]*clicks?", r"total[\s_-]*clicks?",
        r"link[\s_-]*clicks?",
    ],
    "replied": [
        r"^replied?$", r"^repl(?:y|ies)$", r"^responses?$",
        r"reply[\s_-]*count", r"total[\s_-]*replies",
    ],
    "meeting_booked": [
        r"meeting", r"^booked$", r"^demo$", r"call[\s_-]*scheduled",
        r"meetings?[\s_-]*booked", r"demos?[\s_-]*booked",
        r"^appointments?$",
    ],
    "bounced": [
        r"^bounced?$", r"bounce[\s_-]*count", r"^hard[\s_-]*bounce$",
        r"total[\s_-]*bounces",
    ],
    "unsubscribed": [
        r"^unsub", r"opt[\s_-]*out", r"unsubscribe[\s_-]*count",
    ],
}

# Salesloft cadence step export format
# Columns: Name, Day, Type, Bounced, Clicked, Completed, Pending, Scheduled, Sent emails, Total, Viewed
SALESLOFT_ALIASES = {
    "step_name": [r"^name$"],
    "day": [r"^day$"],
    "step_type": [r"^type$"],
    "sent": [r"^sent[\s_-]*emails$"],
    "opened": [r"^viewed$"],
    "clicked": [r"^clicked$"],
    "bounced": [r"^bounced$"],
    "completed": [r"^completed$"],
    "pending": [r"^pending$"],
    "scheduled": [r"^scheduled$"],
    "total": [r"^total$"],
}


# ---------------------------------------------------------------------------
# Auto-detect column mapping
# ---------------------------------------------------------------------------

def auto_detect_mapping(headers: List[str], aliases: dict) -> dict:
    """
    Match CSV headers to canonical field names using regex aliases.
    Returns {canonical_field: csv_header} for detected matches.
    """
    mapping = {}
    used_headers = set()

    for field, patterns in aliases.items():
        for header in headers:
            if header in used_headers:
                continue
            normalized = header.strip().lower()
            for pattern in patterns:
                if re.search(pattern, normalized, re.IGNORECASE):
                    mapping[field] = header
                    used_headers.add(header)
                    break
            if field in mapping:
                break

    return mapping


# ---------------------------------------------------------------------------
# CSV parsing + normalization
# ---------------------------------------------------------------------------

def parse_csv(filepath: str) -> Tuple[List[str], List[dict]]:
    """Parse a CSV file, return (headers, rows_as_dicts)."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    # Detect encoding
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    return headers, rows


def apply_mapping(rows: List[dict], mapping: dict,
                   numeric_fields: Optional[Set[str]] = None) -> List[dict]:
    """
    Normalize rows using the detected mapping.
    Returns rows with canonical field names.
    Numeric fields are converted to int (empty/missing → 0).
    """
    # Invert: {csv_header: canonical_field}
    header_to_field = {v: k for k, v in mapping.items()}
    numeric_fields = numeric_fields or set()

    normalized = []
    for row in rows:
        new_row = {}
        for header, value in row.items():
            if header in header_to_field:
                field = header_to_field[header]
                clean = value.strip() if value else ""
                if field in numeric_fields:
                    # Convert to int, treating empty/non-numeric as 0
                    try:
                        clean = int(float(clean)) if clean else 0
                    except (ValueError, TypeError):
                        clean = 0
                new_row[field] = clean
        normalized.append(new_row)

    return normalized


# Numeric fields that should be converted to int (empty → 0)
SALESLOFT_NUMERIC = {"sent", "opened", "clicked", "bounced", "completed",
                     "pending", "scheduled", "total", "day"}
RESULTS_NUMERIC = {"sent", "opened", "clicked", "replied", "meeting_booked",
                   "bounced", "unsubscribed", "email_number"}


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: csv_parse.py <prospects|results|detect> <filepath>", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    filepath = sys.argv[2]

    headers, rows = parse_csv(filepath)

    # Select alias set and numeric fields based on mode
    if mode == "salesloft":
        aliases = SALESLOFT_ALIASES
        numeric = SALESLOFT_NUMERIC
    elif mode == "results":
        aliases = RESULTS_ALIASES
        numeric = RESULTS_NUMERIC
    else:
        aliases = PROSPECT_ALIASES
        numeric = set()

    mapping = auto_detect_mapping(headers, aliases)

    if mode == "detect":
        print(json.dumps({
            "headers": headers,
            "mapping": mapping,
            "unmapped_headers": [h for h in headers if h not in mapping.values()],
            "unmapped_fields": [f for f in aliases if f not in mapping],
        }, indent=2))
        return

    normalized = apply_mapping(rows, mapping, numeric)

    print(json.dumps({
        "mapping": mapping,
        "row_count": len(normalized),
        "rows": normalized,
    }, indent=2))


if __name__ == "__main__":
    main()
