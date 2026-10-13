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

LLMs make arithmetic slips on pity math. In a test run of the Pity Auditor on its own test case (no code execution), 5 of 22 numbers were wrong, including the featured-character P50 and P90. With `pity_math.py` available, the same test case came back with every number exact. Use [`scripts/pity_math.py`](scripts/pity_math.py) to check any report, or give it to a model that can run code. The Pity Auditor, Sparking vs. Pity Simulator and Lootbox Compliance Generator prompts tell the model to use it.

```bash
# Test case: 0.6% base, +2% per pull from pull 70, hard pity at 90,
# 50/50 split in neutral state, 150 gems per pull, 100 gems = $1
python3 scripts/pity_math.py --base 0.006 --hard 90 --soft-start 70 --soft-step 0.02 \
    --win-rate 0.5 --cost 150 --per-usd 100
```

It prints expected pulls, effective rate, P50, P90 and worst case for the rarity hit and the featured item, plus a 100,000-trial Monte Carlo check, and exits with an error if the exact and simulated means differ by more than 2%. It needs Python 3.8+ and no packages. Run `python3 scripts/pity_math.py --help` for linear, exponential and stepped ramps.

## Try It

[`skills/gacha-pity-auditor/test_case.md`](skills/gacha-pity-auditor/test_case.md) is a sample banner configuration (0.6% base rate, soft pity from pull 70, hard pity at 90, 50/50 rule, neutral state, direct purchase). Load the Gacha Odds & Pity Auditor, paste the test case, and compare its numbers with the `pity_math.py` command above. Exact values: 62.1 expected pulls (1.61%) for any SSR; 93.1 expected pulls, P50 81, P90 155 and worst case 180 for the featured character.

## Installation & Usage

Each skill is a plain-text prompt for use as a system prompt or custom instructions.

1. Open the `SKILL.md` file for the tool you want in the `skills/` directory.
2. Copy the text starting from the `# [Name] - System Prompt` heading.

A current reasoning-capable model works best, for example any current Claude, GPT or Gemini model.

### ChatGPT (Custom GPT)
1. Go to **GPTs** > **Create**, then open the **Configure** tab.
2. Paste the copied text into the **Instructions** box.

The GPT builder limits Instructions to 8,000 characters. The Gacha Odds & Pity Auditor (about 9,300 characters) and Lootbox Compliance Generator (about 8,400) prompts are over that, so for those skills upload `SKILL.md` as a Knowledge file and tell the GPT in Instructions to follow it. Upload `scripts/pity_math.py` as a Knowledge file too and turn on Code Interpreter so the GPT can run it.

### Claude (Projects)
1. Create a new Project in Claude.
2. Paste the copied text into the project's **Instructions**.

### Google Gemini (Gems)
1. In the Gemini app, create a new **Gem**.
2. Paste the copied text into the Gem's **Instructions**.

## License
This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Rahul M Shah.
