#!/usr/bin/env python3
"""Pity math for gacha banners: exact numbers plus a Monte Carlo check.

Hard pity only (no soft pity), the closed form applies:

    expected pulls = (1 - (1 - p)^N) / p
    effective rate = 1 / expected pulls

where p is the base rate per pull and N is the hard pity pull. With soft
pity the per-pull rate changes, so the script builds the exact
distribution of pulls-to-hit pull by pull instead. Either way it
cross-checks the result with a Monte Carlo simulation (100,000 trials by
default).

Examples:
    # 0.8% base, hard pity at 80
    python3 scripts/pity_math.py --base 0.008 --hard 80

    # 0.6% base, +2% per pull from pull 70, hard pity at 90,
    # 50/50 featured split (neutral state), 150 gems per pull, 100 gems = $1
    python3 scripts/pity_math.py --base 0.006 --hard 90 --soft-start 70 \
        --soft-step 0.02 --win-rate 0.5 --cost 150 --per-usd 100

Standard library only. Python 3.8+.
"""

import argparse
import json
import math
import random
import sys


def per_pull_rates(base, hard, soft_start=None, soft_step=0.0, soft_factor=None, overrides=None):
    """Probability of the rarity-tier hit on pull k, for k = 1..hard.

    Linear ramp: rate = base + soft_step * (k - soft_start + 1) for k >= soft_start.
    Exponential ramp: rate = base * soft_factor ** (k - soft_start + 1) for k >= soft_start.
    overrides maps pull number to an explicit rate (stepped ramps).
    The hard pity pull always has rate 1.
    """
    rates = []
    for k in range(1, hard + 1):
        r = base
        if soft_start is not None and k >= soft_start:
            steps = k - soft_start + 1
            if soft_factor is not None:
                r = base * soft_factor ** steps
            else:
                r = base + soft_step * steps
        if overrides and k in overrides:
            r = overrides[k]
        if k == hard:
            r = 1.0
        rates.append(min(r, 1.0))
    return rates


def hit_pmf(rates):
    """pmf[k] = P(first hit on pull k), k = 1..len(rates). Index 0 is unused."""
    pmf = [0.0]
    survive = 1.0
    for r in rates:
        pmf.append(survive * r)
        survive *= 1.0 - r
    return pmf


def convolve(a, b):
    out = [0.0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0.0:
            continue
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def featured_pmf(pmf, win_rate, guaranteed):
    """Pulls to the featured item when a hit is featured with probability
    win_rate and a lost split guarantees the next hit."""
    if guaranteed or win_rate >= 1.0:
        return pmf
    two_cycles = convolve(pmf, pmf)
    out = [0.0] * len(two_cycles)
    for k, x in enumerate(pmf):
        out[k] += win_rate * x
    for k, x in enumerate(two_cycles):
        out[k] += (1.0 - win_rate) * x
    return out


def mean(pmf):
    return sum(k * x for k, x in enumerate(pmf))


def percentile(pmf, q):
    """Smallest k with P(X <= k) >= q."""
    total = 0.0
    for k, x in enumerate(pmf):
        total += x
        if total >= q - 1e-12:
            return k
    return len(pmf) - 1


def worst_case(pmf):
    return max(k for k, x in enumerate(pmf) if x > 0)


def closed_form_expected_pulls(base, hard):
    """Hard pity only: (1 - (1 - p)^N) / p."""
    return (1.0 - (1.0 - base) ** hard) / base


def simulate(rates, win_rate, guaranteed, trials, seed):
    """Monte Carlo: pulls until the hit (and until the featured item)."""
    rng = random.Random(seed)
    hard = len(rates)
    hit_samples, featured_samples = [], []
    for _ in range(trials):
        pulls = 0
        first_hit = None
        is_guaranteed = guaranteed
        while True:
            k = 0
            while True:
                k += 1
                if k == hard or rng.random() < rates[k - 1]:
                    break
            pulls += k
            if first_hit is None:
                first_hit = pulls
            if is_guaranteed or rng.random() < win_rate:
                break
            is_guaranteed = True
        hit_samples.append(first_hit)
        featured_samples.append(pulls)
    return hit_samples, featured_samples


def sample_stats(samples):
    s = sorted(samples)
    n = len(s)
    return {
        "mean": sum(s) / n,
        "p50": s[math.ceil(0.5 * n) - 1],
        "p90": s[math.ceil(0.9 * n) - 1],
        "max": s[-1],
    }


def summarize(pmf):
    m = mean(pmf)
    return {
        "expected_pulls": m,
        "effective_rate": 1.0 / m,
        "p50": percentile(pmf, 0.5),
        "p90": percentile(pmf, 0.9),
        "worst_case": worst_case(pmf),
    }


def parse_overrides(items):
    out = {}
    for item in items or []:
        k, p = item.split("=")
        out[int(k)] = float(p)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", type=float, required=True, help="base rate per pull, as a fraction (0.006 = 0.6%%)")
    ap.add_argument("--hard", type=int, required=True, help="hard pity pull (hit guaranteed on this pull)")
    ap.add_argument("--soft-start", type=int, help="first pull with a boosted rate")
    ap.add_argument("--soft-step", type=float, default=0.0, help="linear ramp: rate added per pull from --soft-start")
    ap.add_argument("--soft-factor", type=float, help="exponential ramp: rate multiplier per pull from --soft-start")
    ap.add_argument("--rate", action="append", metavar="K=P", help="explicit rate P on pull K (stepped ramps); repeatable")
    ap.add_argument("--win-rate", type=float, default=1.0, help="chance a hit is the featured item (0.5 for 50/50; 1 = no split)")
    ap.add_argument("--guaranteed", action="store_true", help="player is in guaranteed state (lost the last split)")
    ap.add_argument("--cost", type=float, help="premium currency per pull")
    ap.add_argument("--per-usd", type=float, help="premium currency per 1 USD")
    ap.add_argument("--trials", type=int, default=100_000, help="Monte Carlo trials (default 100000)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args(argv)

    if not 0.0 < args.base <= 1.0:
        ap.error("--base must be in (0, 1]")
    if args.soft_start is not None and args.soft_start >= args.hard:
        ap.error("--soft-start must be below --hard")
    if not 0.0 < args.win_rate <= 1.0:
        ap.error("--win-rate must be in (0, 1]")

    rates = per_pull_rates(args.base, args.hard, args.soft_start, args.soft_step,
                           args.soft_factor, parse_overrides(args.rate))
    pmf = hit_pmf(rates)
    result = {"inputs": vars(args).copy(), "hit": summarize(pmf)}
    has_soft = args.soft_start is not None or bool(args.rate)
    if not has_soft:
        result["hit"]["closed_form_expected_pulls"] = closed_form_expected_pulls(args.base, args.hard)

    if args.win_rate < 1.0:
        result["featured"] = summarize(featured_pmf(pmf, args.win_rate, args.guaranteed))

    hit_s, feat_s = simulate(rates, args.win_rate, args.guaranteed, args.trials, args.seed)
    result["monte_carlo"] = {"hit": sample_stats(hit_s)}
    if args.win_rate < 1.0:
        result["monte_carlo"]["featured"] = sample_stats(feat_s)

    # Fail loudly if the exact numbers and the simulation disagree.
    checks = [("hit", result["hit"]["expected_pulls"], result["monte_carlo"]["hit"]["mean"])]
    if args.win_rate < 1.0:
        checks.append(("featured", result["featured"]["expected_pulls"], result["monte_carlo"]["featured"]["mean"]))
    for name, exact, sim in checks:
        if abs(exact - sim) / exact > 0.02:
            print(f"error: {name} exact mean {exact:.3f} vs simulated {sim:.3f} differ by more than 2%", file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    def money(pulls):
        parts = [f"{pulls:,.1f} pulls" if isinstance(pulls, float) else f"{pulls:,} pulls"]
        if args.cost:
            cur = pulls * args.cost
            parts.append(f"{cur:,.0f} currency" if float(cur).is_integer() else f"{cur:,.2f} currency")
            if args.per_usd:
                parts.append(f"${cur / args.per_usd:,.2f}")
        return " / ".join(parts)

    def block(title, s, sim):
        print(title)
        print(f"  Expected pulls (mean) : {money(s['expected_pulls'])}   [Monte Carlo {sim['mean']:.2f}]")
        if "closed_form_expected_pulls" in s:
            print(f"  Closed form check     : {s['closed_form_expected_pulls']:.4f} pulls")
        print(f"  Effective rate        : {100 * s['effective_rate']:.3f}%")
        print(f"  P50                   : {money(s['p50'])}   [Monte Carlo {sim['p50']}]")
        print(f"  P90                   : {money(s['p90'])}   [Monte Carlo {sim['p90']}]")
        print(f"  Worst case            : {money(s['worst_case'])}   [Monte Carlo max {sim['max']}]")

    block("Rarity-tier hit (any item at this rarity)", result["hit"], result["monte_carlo"]["hit"])
    if args.win_rate < 1.0:
        state = "guaranteed" if args.guaranteed else "neutral"
        block(f"Featured item ({args.win_rate:.0%} win rate, {state} state)", result["featured"], result["monte_carlo"]["featured"])
    print(f"Monte Carlo: {args.trials:,} trials, seed {args.seed}. Exact and simulated means agree within 2%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
