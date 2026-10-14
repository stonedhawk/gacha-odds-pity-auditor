"""Repository checks. Run: python3 -m unittest discover tests"""

import glob
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_SKILL_CHARS = 7500
PITY_DIR = os.path.join(ROOT, "skills", "gacha-pity-auditor")


class TestSkillLength(unittest.TestCase):
    def test_every_skill_under_limit(self):
        """Each SKILL.md must stay under 7,500 characters so it pastes into a Custom GPT."""
        files = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
        self.assertTrue(files, "no SKILL.md files found")
        for path in files:
            with open(path, encoding="utf-8") as f:
                n = len(f.read())
            self.assertLessEqual(n, MAX_SKILL_CHARS, f"{os.path.relpath(path, ROOT)} is {n} characters")


# Rules each skill must keep, as exact text. If you reword a rule on purpose,
# update the text here in the same change.
TOOLS_RULE = ("If you can run code in this conversation, run scripts/pity_math.py. "
              "If you can't, compute every number yourself and continue.")
NEVER_SEARCH_RULE = "Never search for the script, ask the user for it, or stop to look for it."
RATIO_RULE = "Write every ratio or comparison as the two numbers and their quotient"
PITY_MATH_SKILLS = ["gacha-pity-auditor", "sparking-vs-pity-simulator", "lootbox-compliance-generator"]
REQUIRED_RULES = {
    "gacha-pity-auditor": {
        "50/50 state: fresh": "fresh (no prior 50/50 result on this banner)",
        "50/50 state: guaranteed": "guaranteed (lost the last 50/50, so the next hit is the featured item)",
        "50/50 state: report both if missing": "If missing, report both states side by side.",
        "halt only on design inputs": "Halt with MISSING DATA only if one of these is missing:",
        "halt input: base rate": "1. **Base Rate**",
        "halt input: hard pity": "2. **Hard Pity Threshold**",
        "halt input: soft pity start": "3. **Soft Pity Start**",
        "missing ramp does not halt": "If missing, do not assume a curve: compute with hard pity only",
        "missing purchase method does not halt": "If missing, assume direct purchase at the stated rate.",
        "missing data error": "**[ERROR - MISSING DATA]** only when a banner design input is missing",
    },
    "sparking-vs-pity-simulator": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide base rate, pull cost, hard pity threshold, spark token requirement, or spark earn rate.",
        "spark cost inconsistency": "**[ERROR - SPARK COST INCONSISTENCY]:**",
    },
    "lootbox-compliance-generator": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide base rate or pity thresholds.",
        "illegal mechanic halt": "**[ERROR - ILLEGAL MECHANIC]:**",
    },
    "battle-pass-roi-calculator": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide pass contents or standard shop prices.",
    },
    "kompu-gacha-detector": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide total items in the set, drop rates, and cost per pull.",
    },
    "pool-dilution-calculator": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide current pool size, SSR base rate, or monthly addition rate.",
    },
    "shard-economy-analyzer": {
        "missing data error": "**[ERROR - MISSING DATA]:** If the user does not provide shard threshold, drop type, drop rate/distribution, or cost per pull.",
    },
}
for _skill in PITY_MATH_SKILLS:
    REQUIRED_RULES[_skill]["check-your-tools rule"] = TOOLS_RULE
    REQUIRED_RULES[_skill]["never search for the script"] = NEVER_SEARCH_RULE
    REQUIRED_RULES[_skill]["ratio rule"] = RATIO_RULE


def read_skill(name):
    with open(os.path.join(ROOT, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class TestSkillRules(unittest.TestCase):
    def test_every_skill_is_covered(self):
        on_disk = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md"))}
        self.assertEqual(on_disk, set(REQUIRED_RULES))

    def test_required_rules_present(self):
        """Fails if a SKILL.md loses a required rule (50/50 states, tools, ratios, halt conditions)."""
        for skill, rules in REQUIRED_RULES.items():
            text = read_skill(skill)
            for label, phrase in rules.items():
                with self.subTest(skill=skill, rule=label):
                    self.assertTrue(phrase in text, f"{skill} lost required rule '{label}': expected text: {phrase!r}")

    def test_no_reversed_50_50_definition(self):
        """The guaranteed state follows a lost 50/50, never a won one."""
        for skill in REQUIRED_RULES:
            m = re.search(r"guaranteed[^.\n]{0,40}won (the )?last 50/50", read_skill(skill), re.IGNORECASE)
            self.assertIsNone(m, f"{skill} defines the guaranteed state as following a won 50/50: {m and m.group(0)!r}")


class TestExpectedValues(unittest.TestCase):
    def load(self):
        with open(os.path.join(PITY_DIR, "expected_values.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_expected_values_match_pity_math(self):
        """Each test case's metrics must equal what pity_math.py produces today."""
        stored = self.load()
        for name, case in stored["test_cases"].items():
            cmd = case["generated_by"].split()[1:]  # drop "python3"
            out = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True, check=True)
            fresh = json.loads(out.stdout)
            with self.subTest(case=name):
                self.assertEqual(case["metrics"], fresh["metrics"])
                self.assertEqual(stored["tolerance"], fresh["tolerance"])
                self.assertEqual(case["soft_pity_applied"], "--soft-start" in cmd)

    def test_every_test_case_listed(self):
        listed = set(self.load()["test_cases"])
        on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(PITY_DIR, "test_case*.md"))}
        self.assertEqual(listed, on_disk)


class TestCheckOutput(unittest.TestCase):
    def run_check(self, text, case="test_case.md"):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(text)
        try:
            return subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "check_output.py"), f.name,
                 os.path.join(PITY_DIR, "expected_values.json"), "--case", case],
                capture_output=True, text=True)
        finally:
            os.unlink(f.name)

    # Correct output for test_case.md (ramp given, fresh state).
    GOOD = """The P90 player pays $232.50 / $121.50 = 1.91× the median.
```json
{"pity_numbers": {
 "soft_pity_applied": true,
 "any_item": {"expected_pulls": 62.09, "effective_rate_pct": 1.61, "p50_pulls": 74, "p90_pulls": 82, "max_pulls": 90, "expected_usd": 93.14},
 "featured_fresh": {"expected_pulls": 93.14, "effective_rate_pct": 1.07, "p50_pulls": 81, "p90_pulls": 155, "max_pulls": 180, "p90_usd": 232.5}
}}
```
"""

    # Correct output for test_case_minimal.md (no ramp: hard pity only, both states).
    MINIMAL = """Worst-case cost (soft pity not applied). Fresh vs guaranteed: $156.82 / $104.55 = 1.50×.
[CLARIFICATION NEEDED] What is the soft pity ramp model and step?
```json
{"pity_numbers": {
 "soft_pity_applied": false,
 "any_item": {"expected_pulls": 69.70, "effective_rate_pct": 1.43, "p50_pulls": 90, "p90_pulls": 90, "max_pulls": 90, "expected_usd": 104.55},
 "featured_fresh": {"expected_pulls": 104.55, "effective_rate_pct": 0.96, "p50_pulls": 90, "p90_pulls": 180, "max_pulls": 180},
 "featured_guaranteed": {"expected_pulls": 69.70, "effective_rate_pct": 1.43, "p50_pulls": 90, "p90_pulls": 90, "max_pulls": 90}
}}
```
"""

    def test_correct_output_passes(self):
        r = self.run_check(self.GOOD)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_correct_minimal_output_passes(self):
        r = self.run_check(self.MINIMAL, "test_case_minimal.md")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_wrong_percentile_fails(self):
        r = self.run_check(self.GOOD.replace('"p90_pulls": 155', '"p90_pulls": 154'))
        self.assertEqual(r.returncode, 1)
        self.assertIn("featured_fresh.p90_pulls", r.stdout)

    def test_wrong_ratio_fails(self):
        r = self.run_check(self.GOOD.replace("= 1.91×", "= 2.5×"))
        self.assertEqual(r.returncode, 1)

    def test_bold_ratio_is_recognised(self):
        r = self.run_check(self.GOOD.replace("= 1.91×", "= **1.91×**"))
        self.assertEqual(r.returncode, 0, r.stdout)
        r = self.run_check(self.GOOD.replace("= 1.91×", "= **2.5×**"))
        self.assertEqual(r.returncode, 1)

    def test_bare_comparison_word_fails(self):
        r = self.run_check("Losing the 50/50 is roughly twice as costly.\n" + self.GOOD)
        self.assertEqual(r.returncode, 1)
        self.assertIn("twice", r.stdout)

    def test_labelled_ratio_is_recognised(self):
        r = self.run_check(self.GOOD + "\nFresh P90 ($232.50) / Fresh P50 ($121.50) = 1.91×, so 1.91× it is.\n")
        self.assertEqual(r.returncode, 0, r.stdout)
        r = self.run_check(self.GOOD + "\nFresh P90 ($232.50) / Fresh P50 ($121.50) = 1.50×\n")
        self.assertEqual(r.returncode, 1)

    def test_exponents_are_not_multipliers(self):
        r = self.run_check(self.GOOD + "\nBoth cycles reach hard pity with probability q^89 × q^89.\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_idioms_are_not_comparisons(self):
        r = self.run_check(self.GOOD + "\nFresh losers face double jeopardy at the double-pity ceiling.\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_repeat_of_earlier_full_ratio_passes(self):
        r = self.run_check(self.GOOD + "\nThat 1.91× gap is the main risk; at one decimal it is 1.9×.\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_bare_ratio_before_its_full_form_fails(self):
        r = self.run_check("The gap is 1.91×.\n" + self.GOOD)
        self.assertEqual(r.returncode, 1)

    def test_bare_ratio_not_shown_fails(self):
        r = self.run_check(self.GOOD + "\nLosers pay 2× the cost.\n")  # 2× does not repeat 1.91×
        self.assertEqual(r.returncode, 1)

    def test_minimal_needs_both_states(self):
        r = self.run_check(self.MINIMAL.replace('"featured_guaranteed"', '"unused"'), "test_case_minimal.md")
        self.assertEqual(r.returncode, 1)

    def test_minimal_needs_clarification_and_flag(self):
        r = self.run_check(self.MINIMAL.replace("[CLARIFICATION NEEDED]", ""), "test_case_minimal.md")
        self.assertEqual(r.returncode, 1)
        r = self.run_check(self.MINIMAL.replace('"soft_pity_applied": false', '"soft_pity_applied": true'), "test_case_minimal.md")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
