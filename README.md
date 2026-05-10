# Gacha Odds & Pity Auditor

## Overview
The **Gacha Odds & Pity Auditor** is an advanced cross-LLM AI Skill designed for Game Producers and Economy Designers. 

Hidden costs, broken economies, and perceived unfairness in gacha systems can lead to massive community backlash and player churn. This tool acts as an automated Game Economy Data Scientist, analyzing complex gacha rules (like soft pity, hard pity, and 50/50 mechanics) to expose the true Effective Drop Rate (EDR), real-world Expected Value (EV), and Worst-Case Scenario costs. 

By running your banner configurations through this auditor, you can identify risky tuning thresholds and balance your game economy *before* player outrage occurs.

## Example Use Cases

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

This skill is designed to be used as a System Prompt or Custom GPT instruction.

### ChatGPT (Custom GPT)
1. Go to "Explore" > "Create a GPT".
2. Paste the contents of `system_prompt.md` into the **Instructions** box.
3. Test the GPT by pasting the contents of `test_case_input.md` into the chat.

### Anthropic Claude (Projects / System Prompt)
1. Create a new Project in Claude.
2. Under "Custom Instructions", paste the contents of `system_prompt.md`.
3. Start a new chat within the project and provide the configuration from `test_case_input.md`.

### Google Gemini (Gems / Advanced Prompting)
1. Create a new "Gem" in Gemini Advanced.
2. Paste the `system_prompt.md` into the custom instructions area.
3. Provide the `test_case_input.md` in your first message.

## Files Included
*   `system_prompt.md`: The core instructions that define the AI's persona, calculation requirements, and strict output formatting.
*   `test_case_input.md`: A complex, realistic gacha banner configuration to test the AI's mathematical reasoning.

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
