"""Repository checks. Run: python3 -m unittest discover tests"""

import glob
import json
import os
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


class TestExpectedValues(unittest.TestCase):
    def test_expected_values_match_pity_math(self):
        """expected_values.json must equal what pity_math.py produces today."""
        with open(os.path.join(PITY_DIR, "expected_values.json"), encoding="utf-8") as f:
            stored = json.load(f)
        cmd = stored["generated_by"].split()[1:]  # drop "python3"
        out = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True, check=True)
        fresh = json.loads(out.stdout)
        self.assertEqual(stored["metrics"], fresh["metrics"])
        self.assertEqual(stored["tolerance"], fresh["tolerance"])

    def test_every_test_case_listed(self):
        with open(os.path.join(PITY_DIR, "expected_values.json"), encoding="utf-8") as f:
            listed = set(json.load(f)["test_cases"])
        on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(PITY_DIR, "test_case*.md"))}
        self.assertEqual(listed, on_disk)


class TestCheckOutput(unittest.TestCase):
    def run_check(self, text, case="test_case_minimal.md"):
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

    GOOD = """The P90 player pays $232.50 / $121.50 = 1.91× the median.
```json
{"pity_numbers": {
 "any_item": {"expected_pulls": 62.09, "effective_rate_pct": 1.61, "p50_pulls": 74, "p90_pulls": 82, "max_pulls": 90, "expected_usd": 93.14},
 "featured_fresh": {"expected_pulls": 93.14, "effective_rate_pct": 1.07, "p50_pulls": 81, "p90_pulls": 155, "max_pulls": 180, "p90_usd": 232.5},
 "featured_guaranteed": {"expected_pulls": 62.09, "effective_rate_pct": 1.61, "p50_pulls": 74, "p90_pulls": 82, "max_pulls": 90}
}}
```
"""

    def test_correct_output_passes(self):
        self.assertEqual(self.run_check(self.GOOD).returncode, 0)

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

    def test_bare_comparison_fails(self):
        r = self.run_check("Losing the 50/50 is roughly twice as costly.\n" + self.GOOD)
        self.assertEqual(r.returncode, 1)
        self.assertIn("twice", r.stdout)

    def test_missing_state_fails(self):
        r = self.run_check(self.GOOD.replace('"featured_guaranteed"', '"unused"'))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
