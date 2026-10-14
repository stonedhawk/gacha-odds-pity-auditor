#!/usr/bin/env python3
"""Check a saved Pity Auditor output against expected values.

Three checks:

1. Numbers block. The skill ends its report with a JSON block holding
   {"pity_numbers": {...}}. Every number in it is compared with the
   expected values (written by scripts/pity_math.py --expected), using
   the tolerances stored in the expected-values file:
     - P50, P90 and worst-case pulls: exact
     - expected pulls: +/- 0.1
     - effective rate: +/- 0.01 percentage points
     - currency and USD: +/- 0.5% (covers rounding the mean first)
2. Stated ratios. Every "A / B = R×" in the text must satisfy A / B = R
   within 1% (or the rounding of R, if looser).
3. Bare comparisons. The skill requires both numbers to be shown. A bare
   multiplier ("1.91×") is allowed only if it repeats a ratio shown in
   full earlier in the same output (same value after rounding, and within
   0.05 of it, so "2×" may repeat 2.00× but not 1.50×). A comparison word ("twice", "double", "half", "40% more")
   on a line with no "A / B = R×" is reported.
4. Test-case specifics from expected_values.json: whether soft pity was
   applied, and any text the output must contain (e.g. a clarification
   request when the ramp model is missing).

Usage:
    python3 scripts/check_output.py OUTPUT.md skills/gacha-pity-auditor/expected_values.json \
        --case test_case_minimal.md

Exits 0 if every check passes, 1 otherwise. Standard library only.
"""

import argparse
import json
import re
import sys

NUM = r"\$?\s?\d[\d,]*(?:\.\d+)?"
UNIT = r"(?:\s?(?:%|pulls?|gems?|currency|USD))?"
# Markdown emphasis or code marks may wrap any part: "$123.00 / $111.00 = **1.11×**"
RATIO = re.compile(rf"[*`_]*({NUM}){UNIT}[*`_]*\s*/\s*[*`_]*({NUM}){UNIT}[*`_]*\s*=\s*[*`_]*(\d+(?:\.\d+)?)\s?[×x]")
BARE_MULT = re.compile(r"(?<![\w./])\d+(?:\.\d+)?\s?[×x](?!\s*[\d$(])")
BARE_WORDS = re.compile(
    r"\b(twice|double[sd]?(?!-|\s+jeopardy)|triple[sd]?(?!-)|half as|halves|times as|\d+(?:\.\d+)?%\s+(?:more|less|higher|lower|cheaper|premium|increase|decrease))\b",
    re.IGNORECASE,
)


def to_float(text):
    return float(text.replace("$", "").replace(",", "").strip())


def find_numbers_block(text):
    """Return the last JSON object in the text that contains "pity_numbers"."""
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    for raw in reversed(blocks):
        if "pity_numbers" in raw:
            return json.loads(raw)["pity_numbers"]
    return None


def tolerance_for(key, expected, tol):
    if key.endswith("_pulls") and key != "expected_pulls":
        return tol["percentile_pulls"]
    if key == "expected_pulls":
        return tol["expected_pulls"]
    if key == "effective_rate_pct":
        return tol["effective_rate_pct"]
    return abs(expected) * tol["cost_relative"]


def check_numbers(block, case, tol):
    problems, checked = [], 0
    if block is None:
        return ["no ```json block with \"pity_numbers\" found"], 0
    expected, required = case["metrics"], case["required_groups"]
    block = dict(block)
    applied = block.pop("soft_pity_applied", None)
    if case.get("soft_pity_applied") is not None and applied is not case["soft_pity_applied"]:
        problems.append(f"soft_pity_applied: got {applied!r}, expected {case['soft_pity_applied']}")
    for group in required:
        if not block.get(group):
            problems.append(f"missing group {group}")
    for group, values in block.items():
        if group not in expected:
            problems.append(f"unexpected group {group}")
            continue
        for key, got in values.items():
            if key not in expected[group]:
                continue
            want = expected[group][key]
            checked += 1
            if not isinstance(got, (int, float)):
                problems.append(f"{group}.{key}: {got!r} is not a number")
            elif abs(got - want) > tolerance_for(key, want, tol) + 1e-9:
                problems.append(f"{group}.{key}: got {got}, expected {want}")
        for key in ("expected_pulls", "effective_rate_pct", "p50_pulls", "p90_pulls", "max_pulls"):
            if group in required and key not in values:
                problems.append(f"{group}.{key} missing")
    return problems, checked


def check_text(text, tol):
    """Check stated ratios and bare comparisons, in reading order."""
    ratio_problems, bare, shown = [], [], []
    count = repeats = 0
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        events = []
        spans = []
        for m in RATIO.finditer(line):
            spans.append(m.span())
            events.append((m.start(), "full", m))
        for m in BARE_MULT.finditer(line):
            if not any(a <= m.start() < b for a, b in spans):
                events.append((m.start(), "bare", m))
        for _, kind, m in sorted(events, key=lambda e: e[0]):
            if kind == "full":
                count += 1
                a, b, r = to_float(m.group(1)), to_float(m.group(2)), float(m.group(3))
                decimals = len(m.group(3).split(".")[1]) if "." in m.group(3) else 0
                allowed = max(tol["ratio_relative"] * r, 0.5 * 10 ** -decimals)
                if b == 0 or abs(a / b - r) > allowed + 1e-9:
                    actual = "undefined" if b == 0 else f"{a / b:.3f}"
                    ratio_problems.append(f"line {lineno}: '{m.group(0).strip()}' but {a:g} / {b:g} = {actual}")
                shown.append(r)
            else:
                raw = re.match(r"\d+(?:\.\d+)?", m.group(0)).group(0)
                d = len(raw.split(".")[1]) if "." in raw else 0
                bare_value = float(raw)
                # Same value after rounding, and no further apart than rounding to
                # one decimal allows: "2×" may repeat 2.00×, but not 1.50×.
                if any(f"{v:.{d}f}" == f"{bare_value:.{d}f}" and abs(v - bare_value) <= 0.05 + 1e-9 for v in shown):
                    repeats += 1
                else:
                    bare.append(f"line {lineno}: {m.group(0).strip()} (not shown in full earlier) :: {line.strip()[:120]}")
        if not spans:
            words = [m.group(0) for m in BARE_WORDS.finditer(line)]
            if words:
                bare.append(f"line {lineno}: {', '.join(words)} :: {line.strip()[:120]}")
    return ratio_problems, count, bare, repeats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output", help="saved model output (markdown)")
    ap.add_argument("expected", help="expected_values.json")
    ap.add_argument("--case", required=True, help="test case file name, as listed in expected_values.json")
    args = ap.parse_args(argv)

    text = open(args.output, encoding="utf-8").read()
    spec = json.load(open(args.expected, encoding="utf-8"))
    if args.case not in spec["test_cases"]:
        ap.error(f"--case must be one of: {', '.join(spec['test_cases'])}")
    case = spec["test_cases"][args.case]
    tol = spec["tolerance"]

    num_problems, checked = check_numbers(find_numbers_block(text), case, tol)
    ratio_problems, ratio_count, bare, repeats = check_text(text, tol)
    missing_text = [t for t in case.get("required_text", []) if t.lower() not in text.lower()]

    print(f"Numbers block: {checked} values checked, {len(num_problems)} problem(s)")
    for p in num_problems:
        print(f"  FAIL {p}")
    print(f"Stated ratios: {ratio_count} found, {len(ratio_problems)} wrong")
    for p in ratio_problems:
        print(f"  FAIL {p}")
    print(f"Bare comparisons (no two numbers shown): {len(bare)}, plus {repeats} allowed repeat(s) of ratios shown in full earlier")
    for p in bare:
        print(f"  FAIL {p}")
    print(f"Required text: {len(missing_text)} missing")
    for t in missing_text:
        print(f"  FAIL output does not contain {t!r}")
    failed = bool(num_problems or ratio_problems or bare or missing_text)
    print("RESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
