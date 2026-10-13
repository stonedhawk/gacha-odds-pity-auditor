# Gacha Economy Tool Suite

## Overview
The **Gacha Economy Tool Suite** is a collection of system prompts ("skills") for Game Producers and Economy Designers. Each one is a plain-text prompt you load into an LLM, so it works with any chat model that accepts a system prompt or custom instructions.

Each skill gives the model a persona, the inputs it must collect, the formulas to use, input validation rules and a fixed report format. Together they cover soft pity, hard pity, sparking, shard drops, pool dilution, battle pass value and kompu gacha, and ask the model to report Effective Drop Rate (EDR), Expected Value (EV), cost percentiles (P50/P90/worst case), compliance risk flags and player frustration points.

The model does the math, so check its numbers before you act on them. Three skills (Pity Auditor, Lootbox Compliance Generator, Kompu Gacha Detector) tell the model to run code or a simulation when it can. The skills are not legal or financial advice.

## The Skill Suite

The `skills/` directory contains seven skills:

*   **[Gacha Odds & Pity Auditor](skills/gacha-pity-auditor/SKILL.md):** Analyzes base rates, soft pity, hard pity and the 50/50 rule to calculate Effective Drop Rate (EDR), Expected Value and P50/P90/worst-case cost.
*   **[Sparking vs. Pity Simulator](skills/sparking-vs-pity-simulator/SKILL.md):** Compares the cost distribution, carry-over value and player psychology of "Hard Pity" and "Sparking" (token collection) systems.
*   **[Pool Dilution Calculator](skills/pool-dilution-calculator/SKILL.md):** Projects how the chance of a specific standard-banner item falls as new items are added to the pool, over a 24-month timeline.
*   **[Shard Economy Analyzer](skills/shard-economy-analyzer/SKILL.md):** Analyzes fragment/shard gacha mechanics, calculates mean and P90 pulls to unlock, and estimates "wasted shard" overshoot for variable drops.
*   **[Lootbox Compliance Generator](skills/lootbox-compliance-generator/SKILL.md):** Calculates a "Consolidated Drop Rate" disclosure table and a per-jurisdiction risk check (Apple, Google, Japan, China, Belgium, Netherlands, UK). Have the output reviewed by a lawyer before publishing.
*   **[Kompu Gacha Risk Detector](skills/kompu-gacha-detector/SKILL.md):** Checks event mechanics against the three-condition kompu gacha (complete-the-set) definition and calculates the cost curve of the final missing piece.
*   **[Battle Pass ROI Calculator](skills/battle-pass-roi-calculator/SKILL.md):** Calculates the Premium Currency Equivalent (PCE) per player segment to test whether a Battle Pass's advertised value multiplier holds.

## Try It

[`skills/gacha-pity-auditor/test_case.md`](skills/gacha-pity-auditor/test_case.md) is a sample banner configuration (0.6% base rate, soft pity from pull 70, hard pity at 90, 50/50 rule). Load the Gacha Odds & Pity Auditor, paste the test case, and compare the report against the skill's required output sections.

## Installation & Usage

Each skill is a plain-text prompt for use as a system prompt or custom instructions.

1. Open the `SKILL.md` file for the tool you want in the `skills/` directory.
2. Copy the text starting from the `# [Name] - System Prompt` heading.

A current reasoning-capable model works best, for example any current Claude, GPT or Gemini model.

### ChatGPT (Custom GPT)
1. Go to **GPTs** > **Create**, then open the **Configure** tab.
2. Paste the copied text into the **Instructions** box.

The GPT builder limits Instructions to 8,000 characters. The Gacha Odds & Pity Auditor prompt is about 8,100 characters, so for that skill upload `SKILL.md` as a Knowledge file and tell the GPT in Instructions to follow it.

### Claude (Projects)
1. Create a new Project in Claude.
2. Paste the copied text into the project's **Instructions**.

### Google Gemini (Gems)
1. In the Gemini app, create a new **Gem**.
2. Paste the copied text into the Gem's **Instructions**.

## License
This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Rahul M Shah.
