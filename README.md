# Gacha Economy Tool Suite

## Overview
The **Gacha Economy Tool Suite** is a collection of advanced, cross-LLM AI Skills designed for Game Producers and Economy Designers. 

Hidden costs, broken economies, and perceived unfairness in gacha systems can lead to massive community backlash and player churn. This repository provides a suite of automated Game Economy Data Scientist "Skills." Each tool analyzes complex gacha rules (like soft pity, sparking, shard drops, and kompu gacha) to expose the true Effective Drop Rate (EDR), real-world Expected Value (EV), legal compliance risks, and player frustration points.

By running your monetization configurations through these auditors, you can identify risky tuning thresholds and balance your game economy *before* player outrage occurs.

## The Skill Suite

This repository contains several specialized AI skills located in the `skills/` directory.

*   **[Gacha Odds & Pity Auditor](skills/gacha-pity-auditor/SKILL.md):** Analyzes base rates, soft pity, and hard pity to calculate the true Effective Drop Rate (EDR) and Expected Value.
*   **[Sparking vs. Pity Simulator](skills/sparking-vs-pity-simulator/SKILL.md):** Compares the economic and psychological differences between "Hard Pity" and "Sparking" (token collection) mechanics.
*   **[Pool Dilution Calculator](skills/pool-dilution-calculator/SKILL.md):** Calculates the probability drop-off over time as new characters are permanently added to a standard banner.
*   **[Shard Economy Analyzer](skills/shard-economy-analyzer/SKILL.md):** Analyzes fragment/shard gacha mechanics, calculates average pulls to unlock, and predicts "wasted shard" frustration.
*   **[Lootbox Compliance Generator](skills/lootbox-compliance-generator/SKILL.md):** Formats drop rates into legally compliant "Consolidated Drop Rate" tables for App Store and EU regulations.
*   **[Kompu Gacha Risk Detector](skills/kompu-gacha-detector/SKILL.md):** Audits event mechanics for complete-the-set traits, calculating the exponential cost curve of the final missing piece.
*   **[Battle Pass ROI Calculator](skills/battle-pass-roi-calculator/SKILL.md):** Calculates the Premium Currency Equivalent (PCE) to determine if a Battle Pass's stated value multiplier is accurate.

## Example Use Cases (Gacha Pity Auditor)

The auditor adapts to various monetization models and economic complexities. Below are two hypothetical examples demonstrating how the auditor dissects mechanics and uncovers hidden risks.

| Metric | "Celestial Protocol" (Midcore RPG) | "Merge Mayor Tycoon" (Hybrid Casual) |
| :--- | :--- | :--- |
| **Genre & Monetization** | Character-collector Gacha. High ARPDAU, deep economy. | Merge/Idle game. Ads + microtransactions, broad appeal. |
| **Gacha Structure** | "Weapon Banner" with a 0.8% base rate. Soft pity at 60 pulls, hard pity at 80. Features a 75/25 win/loss ratio. | "Mystery Lootbox" with a 2% base rate for a Legendary item. No soft pity. Hard pity at 50 boxes. |
| **Cost Per Pull** | $2.50 USD (Premium Currency) | $0.99 USD (Direct purchase or earned via gameplay) |
| **Auditor Discovery (EDR)** | Calculates the true drop rate at ~1.4% due to the aggressive soft pity curve. | Calculates EDR exactly at 2.0% until pull 50, showing the pity is a hard safety net rather than a rate boost. |
| **Identified Risk**| **Economy Risk:** The 75/25 split combined with the early soft pity (60) makes weapons *too cheap* on average. Whales will max out the system faster than expected, reducing the long-term revenue tail. | **Player Experience Risk:** Because there is no soft pity, players face a severe "luck gap." A lucky player spends $1, while an unlucky player spends $50. High risk of churn for non-whales who hit the $50 ceiling. |
| **Recommended Action** | *Recommendation:* Shift soft pity to 65 pulls and adjust the rate curve to protect the perceived premium value of weapons. | *Recommendation:* Introduce a mild soft pity at 35 pulls to smooth out the distribution and prevent the extreme $1 vs $50 disparity, keeping casual spenders engaged. |

## Installation & Usage

These skills are completely platform-agnostic and are designed to be used as System Prompts or Custom GPT instructions.

1. Navigate to the `skills/` directory and open the `SKILL.md` file for the tool you want to use.
2. Copy the text starting from `# [Name] - System Prompt`.

### ChatGPT (Custom GPT)
1. Go to "Explore" > "Create a GPT".
2. Paste the copied `SKILL.md` contents into the **Instructions** box.

### Anthropic Claude (Projects / System Prompt)
1. Create a new Project in Claude.
2. Under "Custom Instructions", paste the `SKILL.md` contents.

### Google Gemini (Gems / Advanced Prompting)
1. Create a new "Gem" in Gemini Advanced.
2. Paste the `SKILL.md` into the custom instructions area.

## License
This project is licensed under the MIT License - see below for details.

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
