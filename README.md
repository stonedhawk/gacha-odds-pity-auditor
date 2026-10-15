# Gacha Economy Tool Suite

## Overview
The **Gacha Economy Tool Suite** is a collection of system prompts ("skills") for Game Producers and Economy Designers. Each one is a plain-text prompt you load into an LLM, so it works with any chat model that accepts a system prompt or custom instructions.

Each skill gives the model a persona, the inputs it must collect, the formulas to use, input validation rules and a fixed report format. Together they cover soft pity, hard pity, sparking, shard drops, pool dilution, battle pass value and kompu gacha, and ask the model to report Effective Drop Rate (EDR), Expected Value (EV), cost percentiles (P50/P90/worst case), compliance risk flags and player frustration points.

The model does the math, so check its numbers before you act on them (see Checking the Math). Three skills (Pity Auditor, Lootbox Compliance Generator, Kompu Gacha Detector) tell the model to run code or a simulation when it can. The skills are not legal or financial advice.

## The Skill Suite

The `skills/` directory contains seven skills:

*   **[Gacha Odds & Pity Auditor](skills/gacha-pity-auditor/SKILL.md):** Analyzes base rates, soft pity, hard pity and the 50/50 rule to calculate Effective Drop Rate (EDR), Expected Value and P50/P90/worst-case cost.
*   **[Sparking vs. Pity Simulator](skills/sparking-vs-pity-simulator/SKILL.md):** Compares the cost distribution, carry-over value and player psychology of "Hard Pity" and "Sparking" (token collection) systems.
*   **[Pool Dilution Calculator](skills/pool-dilution-calculator/SKILL.md):** Projects how the chance of a specific standard-banner item falls as new items are added to the pool, over a 24-month timeline.
*   **[Shard Economy Analyzer](skills/shard-economy-analyzer/SKILL.md):** Analyzes fragment/shard gacha mechanics, calculates mean and P90 pulls to unlock, and estimates "wasted shard" overshoot for variable drops.
*   **[Lootbox Compliance Generator](skills/lootbox-compliance-generator/SKILL.md):** Calculates a "Consolidated Drop Rate" disclosure table and a per-jurisdiction risk check (Apple, Google, Japan, China, Belgium, Netherlands, UK). Have the output reviewed by a lawyer before publishing.
*   **[Kompu Gacha Risk Detector](skills/kompu-gacha-detector/SKILL.md):** Checks event mechanics against the three-condition kompu gacha (complete-the-set) definition and calculates the cost curve of the final missing piece.
*   **[Battle Pass ROI Calculator](skills/battle-pass-roi-calculator/SKILL.md):** Calculates the Premium Currency Equivalent (PCE) per player segment to test whether a Battle Pass's advertised value multiplier holds.

## Example Use Cases (Gacha Pity Auditor)

Two hypothetical banners. The effective rates and costs below are computed with the formula under the table and checked with `scripts/pity_math.py`. The risk and recommendation rows are illustrative judgments, not model output.

| Metric | "Celestial Protocol" (Midcore RPG) | "Merge Mayor Tycoon" (Hybrid Casual) |
| :--- | :--- | :--- |
| **Genre & Monetization** | Character-collector Gacha. High ARPDAU, deep economy. | Merge/Idle game. Ads + microtransactions, broad appeal. |
| **Gacha Structure** | "Weapon Banner" with a 0.8% base rate. Soft pity at 60 pulls, hard pity at 80. Features a 75/25 win/loss ratio. | "Mystery Lootbox" with a 2% base rate for a Legendary item. No soft pity. Hard pity at 50 boxes. |
| **Cost Per Pull** | $2.50 USD (Premium Currency) | $0.99 USD (Direct purchase or earned via gameplay) |
| **Effective Drop Rate (EDR)** | 1.69% from hard pity alone (59.3 expected pulls, about $148). Soft pity from pull 60 raises the rate further; the exact figure depends on the ramp model. | 3.15% (31.8 expected boxes, about $31.47). The 2% base rate understates the real rate because hard pity at 50 lifts it. |
| **Cost Spread** | Ignoring soft pity: median 80 pulls ($200) and worst case 80 pulls ($200), because 53% of players reach pull 80 without a hit. Soft pity pulls the median below 80. | Median 35 boxes ($34.65), P90 50 boxes ($49.50), worst case 50 boxes ($49.50). |
| **Identified Risk** | **Economy Risk:** The 75/25 split combined with the early soft pity (60) makes weapons *too cheap* on average. Whales will max out the system faster than expected, reducing the long-term revenue tail. | **Player Experience Risk:** Because there is no soft pity, players face a severe "luck gap." A lucky player spends $0.99, while an unlucky player spends $49.50. High risk of churn for non-whales who hit the ceiling. |
| **Recommended Action** | *Recommendation:* Shift soft pity to 65 pulls and adjust the rate curve to protect the perceived premium value of weapons. | *Recommendation:* Introduce a mild soft pity at 35 boxes to smooth out the distribution and narrow the $0.99 to $49.50 spread, keeping casual spenders engaged. |

With base rate `p` and hard pity on pull `N` (no soft pity):

```
expected pulls = (1 - (1 - p)^N) / p
effective rate = 1 / expected pulls

Celestial Protocol: (1 - 0.992^80) / 0.008 = 59.26 pulls  ->  1 / 59.26 = 1.69%
Merge Mayor:        (1 - 0.98^50)  / 0.02  = 31.79 boxes  ->  1 / 31.79 = 3.15%
```

Soft pity changes the per-pull rate, so the closed form no longer applies. `scripts/pity_math.py` computes the exact distribution pull by pull for any ramp.

## Checking the Math

LLMs make arithmetic slips on pity math. A chat run without the script can be off by about 2% on pull counts and dollar figures (the largest miss in our test runs was 1.3%: a P90 of 153 pulls against an exact 155). For exact numbers, use [`scripts/pity_math.py`](scripts/pity_math.py). Use it to check any report, or give it to a model that can run code. The Pity Auditor, Sparking vs. Pity Simulator and Lootbox Compliance Generator prompts tell the model to use it when it has a code tool, to flag its numbers as unverified when it does not, and to write every ratio as the two numbers it divides (`$232.50 / $121.50 = 1.91×`).

```bash
# Test case: 0.6% base, +2% per pull from pull 70, hard pity at 90,
# 50/50 split, 150 gems per pull, 100 gems = $1
python3 scripts/pity_math.py --base 0.006 --hard 90 --soft-start 70 --soft-step 0.02 \
    --win-rate 0.5 --cost 150 --per-usd 100
```

It prints expected pulls, effective rate, P50, P90 and worst case for the rarity hit and the featured item, plus a 100,000-trial Monte Carlo check, and exits with an error if the exact and simulated means differ by more than 2%. Add `--expected` to print fresh and guaranteed 50/50 states side by side in the format `check_output.py` reads. It needs Python 3.8+ and no packages. Run `python3 scripts/pity_math.py --help` for linear, exponential and stepped ramps.

### Checking a saved model output

The Pity Auditor ends every report with a JSON numbers block. [`scripts/check_output.py`](scripts/check_output.py) compares that block with the test case's entry in [`skills/gacha-pity-auditor/expected_values.json`](skills/gacha-pity-auditor/expected_values.json) (generated by `pity_math.py --expected`), checks every stated ratio, and flags comparisons that do not show their two numbers. A bare multiplier such as `1.91×` passes only if the same ratio was shown in full earlier in the output. For the minimal test case it also checks that soft pity was not applied and that the output asks for the ramp:

```bash
python3 scripts/check_output.py my_output.md skills/gacha-pity-auditor/expected_values.json \
    --case test_case_minimal.md
```

Tolerances: P50, P90 and worst-case pulls must match exactly; expected pulls within 0.1; effective rate within 0.01 percentage points; currency and USD within 0.5%; a stated ratio within 1% of the quotient of its two numbers. It exits 1 on any failure.

**Test results.** In the five latest test runs with no code tool (Claude through the Claude Code CLI), three produced a full report: one on `test_case.md` and two on `test_case_minimal.md`. All three pass `check_output.py` with every number exact, and the minimal runs correctly fell back to hard-pity-only worst-case costs and asked for the ramp. The other two stopped at the start, announcing they would look for `pity_math.py` instead of computing. The CLI adds environment context that an ordinary chat does not, which is the likely cause. In chat apps, 6 of 6 runs on `test_case_minimal.md` finished with every number exact (see Known limitations). In earlier runs, before the prompt changes, one report had four wrong numbers.

## Try It

Two test cases describe the same banner (0.6% base rate, soft pity from pull 70, hard pity at 90, 50/50 rule, 150 gems per pull, 100 gems = $1):

- [`test_case.md`](skills/gacha-pity-auditor/test_case.md) gives every input: a linear ramp of +2% per pull, a fresh 50/50 state and direct purchase. Exact values: any SSR 62.1 expected pulls (1.61%), P50 74, P90 82, worst case 90. Featured character, fresh state: 93.1 expected pulls (1.07%), P50 81, P90 155, worst case 180.
- [`test_case_minimal.md`](skills/gacha-pity-auditor/test_case_minimal.md) leaves out the soft pity ramp, the 50/50 state and the purchase method. The skill should still finish: it computes with hard pity only and labels the figures worst-case costs (soft pity can only lower them), reports fresh and guaranteed states side by side, assumes direct purchase, and asks for the ramp. Exact worst-case values: any SSR 69.7 expected pulls (1.43%), P50, P90 and worst case all 90 pulls ($135.00). Featured character, fresh state: 104.5 expected pulls ($156.82), P50 90, P90 180, worst case 180.

The Pity Auditor halts only when a banner design input is missing: base rate, hard pity threshold, or soft pity start. For anything else, including the ramp, it states a default in Section 0 and continues.

## Installation & Usage

Each skill is a plain-text prompt for use as a system prompt or custom instructions.

1. Open the `SKILL.md` file for the tool you want in the `skills/` directory.
2. Copy the text starting from the `# [Name] - System Prompt` heading.

A current reasoning-capable model works best, for example any current Claude, GPT or Gemini model.

### ChatGPT (Custom GPT)
1. Go to **GPTs** > **Create**, then open the **Configure** tab.
2. Paste the copied text into the **Instructions** box.

Every `SKILL.md` is under 7,500 characters (a test enforces this), so each fits the GPT builder's 8,000-character Instructions limit. To let the GPT run the pity math itself, also upload `scripts/pity_math.py` as a Knowledge file and turn on Code Interpreter.

### Claude (Projects)
1. Create a new Project in Claude.
2. Paste the copied text into the project's **Instructions**.

### Google Gemini (Gems)
1. In the Gemini app, create a new **Gem**.
2. Paste the copied text into the Gem's **Instructions**.

## Known limitations

- **Runs through the Claude Code CLI can stop instead of computing.** In 6 runs of `test_case_minimal.md` through the CLI with no code tool, 4 finished with every number exact; 2 stopped at the start, saying they would run or look for `scripts/pity_math.py`. The CLI adds environment details that make the model believe it can run code. If a run stops, ask the model to compute the numbers itself.
- **Chat apps finished every run.** In October 2026, `test_case_minimal.md` ran 3 times in a Claude Project (code execution on) and 3 times in a ChatGPT Project, with the Pity Auditor prompt as the project instructions. All 6 finished. All 6 numbers blocks pass `check_output.py` with every value exact, all 6 use hard pity only, and all 6 ask for the ramp. Two of the Claude runs first tried to run `scripts/pity_math.py`, then computed the numbers themselves when it was missing.
- **Ratio formatting can slip.** In 2 of those 6 chat runs, `check_output.py` flagged one ratio line each: one put a word between the two numbers (`EDR 1.43% / base 0.60% = 2.39×`), and one showed `2.00×` in a summary card before writing the ratio out in full. Both values were correct.

## License
This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Rahul M Shah.
