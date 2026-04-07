#!/usr/bin/env python3
"""
Statistical analysis for A/B experiment results.

Provides z-test for two proportions, confidence intervals,
and minimum sample size calculations. Designed to be called
by Claude Code skills via bash.

Usage:
  # Compare two variants
  python3 scripts/stats.py compare '{"a_successes":42,"a_total":150,"b_successes":55,"b_total":148}'

  # Full experiment analysis from results file
  python3 scripts/stats.py analyze data/experiments/exp-001-results.json

  # Minimum sample size calculation
  python3 scripts/stats.py sample-size '{"baseline_rate":0.25,"mde":0.05}'
"""

import json
import math
import sys


# ---------------------------------------------------------------------------
# Core statistical functions
# ---------------------------------------------------------------------------

def z_test_proportions(a_successes: int, a_total: int,
                       b_successes: int, b_total: int) -> dict:
    """
    Two-proportion z-test. Tests whether variant B's rate differs
    significantly from variant A's rate.

    Returns z-score, p-value, significance level, and a human-readable label.
    """
    if a_total == 0 or b_total == 0:
        return {
            "z_score": 0, "p_value": 1.0,
            "significant": False, "label": "No data",
            "confidence_level": 0
        }

    p_a = a_successes / a_total
    p_b = b_successes / b_total

    # Pooled proportion under H0: p_a == p_b
    p_pool = (a_successes + b_successes) / (a_total + b_total)

    # Standard error of the difference
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / a_total + 1 / b_total))

    if se == 0:
        return {
            "z_score": 0, "p_value": 1.0,
            "significant": False, "label": "No variance",
            "confidence_level": 0
        }

    z = (p_b - p_a) / se

    # Two-tailed p-value using normal CDF approximation
    p_value = 2 * (1 - normal_cdf(abs(z)))

    # Determine significance tier
    if p_value < 0.05:
        label = f"Significant (p={p_value:.3f})"
        significant = True
        confidence_level = 95
    elif p_value < 0.10:
        label = f"Marginal (p={p_value:.3f})"
        significant = False
        confidence_level = 90
    else:
        label = f"Not significant (p={p_value:.3f})"
        significant = False
        confidence_level = 0

    return {
        "z_score": round(z, 4),
        "p_value": round(p_value, 4),
        "significant": significant,
        "label": label,
        "confidence_level": confidence_level
    }


def confidence_interval(successes: int, total: int,
                        confidence: float = 0.95) -> dict:
    """
    Wilson score confidence interval for a proportion.
    More accurate than the normal approximation for small samples.
    """
    if total == 0:
        return {"lower": 0, "upper": 0, "point": 0}

    z = normal_ppf((1 + confidence) / 2)
    p = successes / total

    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator

    return {
        "lower": round(max(0, center - spread), 4),
        "upper": round(min(1, center + spread), 4),
        "point": round(p, 4)
    }


def minimum_sample_size(baseline_rate: float, mde: float,
                        power: float = 0.8, significance: float = 0.05) -> int:
    """
    Minimum sample size per variant to detect a given effect.

    Args:
        baseline_rate: Current conversion rate (e.g., 0.25 for 25%)
        mde: Minimum detectable effect as absolute difference (e.g., 0.05)
        power: Statistical power (default 0.8)
        significance: Significance level (default 0.05)
    """
    if mde == 0:
        return 0

    z_alpha = normal_ppf(1 - significance / 2)
    z_beta = normal_ppf(power)

    p1 = baseline_rate
    p2 = baseline_rate + mde

    n = ((z_alpha * math.sqrt(2 * p1 * (1 - p1)) +
          z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (mde ** 2)

    return math.ceil(n)


# ---------------------------------------------------------------------------
# Experiment analysis — processes a full results file
# ---------------------------------------------------------------------------

def analyze_experiment(results: list) -> dict:
    """
    Takes a list of result rows (each with variant, sent, opened, replied,
    clicked, meeting_booked) and produces per-variant metrics + significance.
    """
    # Aggregate by variant
    variants = {}
    for row in results:
        v = row.get("variant", "?")
        if v not in variants:
            variants[v] = {
                "sent": 0, "opened": 0, "clicked": 0,
                "replied": 0, "meeting_booked": 0,
                "bounced": 0, "unsubscribed": 0
            }
        for metric in variants[v]:
            variants[v][metric] += int(row.get(metric, 0))

    # Compute rates per variant
    metrics_by_variant = {}
    for v, totals in variants.items():
        sent = totals["sent"]
        metrics_by_variant[v] = {
            "totals": totals,
            "rates": {
                "open_rate": round(totals["opened"] / sent, 4) if sent else 0,
                "reply_rate": round(totals["replied"] / sent, 4) if sent else 0,
                "click_rate": round(totals["clicked"] / sent, 4) if sent else 0,
                "meeting_rate": round(totals["meeting_booked"] / sent, 4) if sent else 0,
                "bounce_rate": round(totals["bounced"] / sent, 4) if sent else 0,
            }
        }

    # Statistical comparison (only if exactly 2 variants)
    variant_keys = sorted(variants.keys())
    comparison = {}
    winner = None

    if len(variant_keys) == 2:
        a_key, b_key = variant_keys
        a, b = variants[a_key], variants[b_key]

        rate_metrics = [
            ("open_rate", "opened"),
            ("reply_rate", "replied"),
            ("click_rate", "clicked"),
            ("meeting_rate", "meeting_booked"),
        ]

        for rate_name, count_field in rate_metrics:
            test = z_test_proportions(
                a[count_field], a["sent"],
                b[count_field], b["sent"]
            )
            ci_a = confidence_interval(a[count_field], a["sent"])
            ci_b = confidence_interval(b[count_field], b["sent"])

            diff = (metrics_by_variant[b_key]["rates"][rate_name] -
                    metrics_by_variant[a_key]["rates"][rate_name])

            comparison[rate_name] = {
                "test": test,
                "ci_a": ci_a,
                "ci_b": ci_b,
                "diff": round(diff, 4),
                "diff_pp": f"{diff * 100:+.1f}pp",
            }

        # Declare winner on primary metric (reply_rate) if significant
        reply_test = comparison.get("reply_rate", {}).get("test", {})
        if reply_test.get("significant"):
            a_rate = metrics_by_variant[a_key]["rates"]["reply_rate"]
            b_rate = metrics_by_variant[b_key]["rates"]["reply_rate"]
            winner = b_key if b_rate > a_rate else a_key

    # Sample size check
    total_sent = sum(v["sent"] for v in variants.values())
    sample_adequate = total_sent >= 60  # At least 30 per variant

    # Determine primary metric for winner: use open_rate if reply data unavailable
    if winner is None and comparison:
        open_test = comparison.get("open_rate", {}).get("test", {})
        if open_test.get("significant"):
            a_rate = metrics_by_variant[variant_keys[0]]["rates"]["open_rate"]
            b_rate = metrics_by_variant[variant_keys[1]]["rates"]["open_rate"]
            winner = variant_keys[1] if b_rate > a_rate else variant_keys[0]
            winner_metric = "open_rate"
        else:
            winner_metric = None
    else:
        winner_metric = "reply_rate" if winner else None

    return {
        "variants": metrics_by_variant,
        "comparison": comparison,
        "winner": winner,
        "winner_metric": winner_metric,
        "sample_adequate": sample_adequate,
        "total_sent": total_sent,
    }


def analyze_salesloft(variant_a_rows: list, variant_b_rows: list,
                      label_a: str = "A", label_b: str = "B") -> dict:
    """
    Analyze two Salesloft cadence step exports (one per variant).
    Each input is a list of step rows with: step_name, sent, opened, clicked, bounced.
    Aggregates across steps, then compares variants.
    """
    def aggregate_steps(rows: list) -> dict:
        totals = {"sent": 0, "opened": 0, "clicked": 0,
                  "bounced": 0, "replied": 0, "meeting_booked": 0}
        for row in rows:
            totals["sent"] += int(row.get("sent", 0))
            totals["opened"] += int(row.get("opened", 0))
            totals["clicked"] += int(row.get("clicked", 0))
            totals["bounced"] += int(row.get("bounced", 0))
            # Salesloft doesn't export replies — leave as 0
            totals["replied"] += int(row.get("replied", 0))
            totals["meeting_booked"] += int(row.get("meeting_booked", 0))
        return totals

    a_totals = aggregate_steps(variant_a_rows)
    b_totals = aggregate_steps(variant_b_rows)

    # Build the format analyze_experiment expects
    combined = [
        {**a_totals, "variant": label_a},
        {**b_totals, "variant": label_b},
    ]

    return analyze_experiment(combined)


# ---------------------------------------------------------------------------
# Math helpers — normal distribution without scipy
# ---------------------------------------------------------------------------

def normal_cdf(x: float) -> float:
    """Standard normal CDF using Abramowitz & Stegun approximation."""
    a1, a2, a3, a4, a5 = (
        0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    )
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x = abs(x) / math.sqrt(2)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * y)


def normal_ppf(p: float) -> float:
    """Inverse normal CDF (percent point function). Rational approximation."""
    if p <= 0:
        return -float('inf')
    if p >= 1:
        return float('inf')
    if p == 0.5:
        return 0.0

    # Rational approximation by Peter Acklam
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]

    p_low = 0.02425
    p_high = 1 - p_low

    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: stats.py <command> [args]", file=sys.stderr)
        print("Commands: compare, analyze, sample-size", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "compare":
        data = json.loads(sys.argv[2])
        result = z_test_proportions(
            data["a_successes"], data["a_total"],
            data["b_successes"], data["b_total"]
        )
        print(json.dumps(result, indent=2))

    elif command == "analyze":
        filepath = sys.argv[2]
        with open(filepath) as f:
            results = json.load(f)
        analysis = analyze_experiment(results)
        print(json.dumps(analysis, indent=2))

    elif command == "analyze-salesloft":
        # Usage: stats.py analyze-salesloft A variant-a.json B variant-b.json
        if len(sys.argv) < 6:
            print("Usage: stats.py analyze-salesloft A file-a.json B file-b.json",
                  file=sys.stderr)
            sys.exit(1)
        label_a, file_a = sys.argv[2], sys.argv[3]
        label_b, file_b = sys.argv[4], sys.argv[5]
        with open(file_a) as f:
            rows_a = json.load(f)
        with open(file_b) as f:
            rows_b = json.load(f)
        # Handle both raw rows and parsed output from csv_parse.py
        if isinstance(rows_a, dict):
            rows_a = rows_a.get("rows", [])
        if isinstance(rows_b, dict):
            rows_b = rows_b.get("rows", [])
        analysis = analyze_salesloft(rows_a, rows_b, label_a, label_b)
        print(json.dumps(analysis, indent=2))

    elif command == "sample-size":
        data = json.loads(sys.argv[2])
        n = minimum_sample_size(
            data["baseline_rate"],
            data["mde"],
            data.get("power", 0.8),
            data.get("significance", 0.05)
        )
        print(json.dumps({"min_sample_per_variant": n}))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
