#!/usr/bin/env python3
"""
CSV exporter for sequences and experiment results.

Reads JSON from stdin or a file and outputs CSV to stdout or a file.

Usage:
  # Export sequences
  python3 scripts/csv_export.py sequences data/sequences/exp-001/ -o export.csv

  # Export experiment results
  python3 scripts/csv_export.py results data/experiments/exp-001-metrics.json -o export.csv

  # Pipe JSON from stdin
  cat data.json | python3 scripts/csv_export.py sequences - -o export.csv
"""

import csv
import json
import sys
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Sequence export — combines variant files into one CSV
# ---------------------------------------------------------------------------

MAX_EMAILS = 5  # Default sequence length; columns adjust dynamically


def build_sequence_columns(num_emails: int) -> List[str]:
    """
    Build column list with flattened email columns.
    One row per variant per prospect: subject_1, body_1, subject_2, body_2, ...
    """
    cols = [
        "experiment_id", "variant", "variant_angle",
        "prospect_company", "contact_name", "prospect_email",
    ]
    for i in range(1, num_emails + 1):
        cols.append(f"subject_{i}")
        cols.append(f"body_{i}")
    return cols


def export_sequences(source: str, output_path: Optional[str]):
    """
    Export sequences from a directory containing variant-a.json and variant-b.json.
    Each variant becomes one row with all emails flattened into columns:
    subject_1, body_1, subject_2, body_2, ... subject_N, body_N
    """
    source_path = Path(source)

    if source_path.is_dir():
        rows = []
        experiment_id = source_path.name
        max_emails = 0

        for variant_file in sorted(source_path.glob("variant-*.json")):
            with open(variant_file) as f:
                data = json.load(f)

            variant = data.get("variant", "?")
            angle = data.get("angle", "")
            prospect = data.get("prospect", {})
            emails = data.get("emails", [])

            # Track max email count for column generation
            max_emails = max(max_emails, len(emails))

            # Build a single row with all emails as columns
            row = {
                "experiment_id": experiment_id,
                "variant": variant,
                "variant_angle": angle,
                "prospect_company": prospect.get("company_name", ""),
                "contact_name": prospect.get("contact_name", ""),
                "prospect_email": prospect.get("contact_email", ""),
            }

            # Flatten emails: sort by number, then assign to subject_N / body_N
            for email in sorted(emails, key=lambda e: e.get("number", 0)):
                n = email.get("number", 0)
                row[f"subject_{n}"] = email.get("subject", "")
                row[f"body_{n}"] = email.get("body", "")

            rows.append(row)
    else:
        # Read from file or stdin
        if source == "-":
            data = json.load(sys.stdin)
        else:
            with open(source) as f:
                data = json.load(f)
        rows = data if isinstance(data, list) else data.get("rows", [])
        max_emails = MAX_EMAILS

    columns = build_sequence_columns(max_emails or MAX_EMAILS)
    write_csv(columns, rows, output_path)


# ---------------------------------------------------------------------------
# Results export — experiment metrics as CSV
# ---------------------------------------------------------------------------

RESULTS_COLUMNS = [
    "variant", "total_sent", "total_opened", "total_replied",
    "total_clicked", "total_meetings",
    "open_rate", "reply_rate", "click_rate", "meeting_rate",
]

def export_results(source: str, output_path: Optional[str]):
    """Export experiment metrics from a metrics JSON file."""
    if source == "-":
        data = json.load(sys.stdin)
    else:
        with open(source) as f:
            data = json.load(f)

    rows = []
    variants = data.get("variants", {})
    for variant_key, variant_data in sorted(variants.items()):
        totals = variant_data.get("totals", {})
        rates = variant_data.get("rates", {})
        rows.append({
            "variant": variant_key,
            "total_sent": totals.get("sent", 0),
            "total_opened": totals.get("opened", 0),
            "total_replied": totals.get("replied", 0),
            "total_clicked": totals.get("clicked", 0),
            "total_meetings": totals.get("meeting_booked", 0),
            "open_rate": f"{rates.get('open_rate', 0):.1%}",
            "reply_rate": f"{rates.get('reply_rate', 0):.1%}",
            "click_rate": f"{rates.get('click_rate', 0):.1%}",
            "meeting_rate": f"{rates.get('meeting_rate', 0):.1%}",
        })

    write_csv(RESULTS_COLUMNS, rows, output_path)


# ---------------------------------------------------------------------------
# Shared CSV writer
# ---------------------------------------------------------------------------

def write_csv(columns: List[str], rows: List[dict], output_path: Optional[str]):
    """Write rows to CSV file or stdout."""
    if output_path:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Exported {len(rows)} rows to {output_path}", file=sys.stderr)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: csv_export.py <sequences|results> <source> [-o output.csv]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    source = sys.argv[2]
    output_path = None

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if mode == "sequences":
        export_sequences(source, output_path)
    elif mode == "results":
        export_results(source, output_path)
    else:
        print(f"Unknown mode: {mode}. Use 'sequences' or 'results'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
