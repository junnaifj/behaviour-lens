import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from vault_store import get_observations_by_period, save_observation, save_pattern_review, search_observations


class VaultStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def observation(self, day="2026-09-25", text="People check reviews before choosing lunch"):
        return save_observation({"observation": text, "brief": "## Evidence status\n\nUncertain.", "date": day, "evidence_status": "uncertain", "domain": ["consumer-behaviour"], "analytical_scale": ["individual"], "sources": [{"title": "Example", "url": "https://example.org"}]}, self.root)

    def test_save_search_and_period(self):
        saved = self.observation()
        self.assertTrue(Path(saved["path"]).exists())
        found = search_observations("reviews lunch", root=self.root)
        self.assertEqual(found["count"], 1)
        period = get_observations_by_period("2026-09-01", "2026-09-30", root=self.root)
        self.assertEqual(period["observations"][0]["id"], saved["id"])
        self.assertIn("Raw observation", period["observations"][0]["content"])

    def test_period_is_inclusive_and_filterable(self):
        self.observation("2026-09-01")
        self.observation("2026-09-30", "People imitate queue choices")
        self.assertEqual(get_observations_by_period("2026-09-01", "2026-09-30", root=self.root)["count"], 2)
        self.assertEqual(search_observations(filters={"domain": "consumer-behaviour"}, root=self.root)["count"], 2)

    def test_review_records_caution(self):
        saved = self.observation()
        review = save_pattern_review({"review_type": "weekly", "period_start": "2026-09-21", "period_end": "2026-09-27", "review": "One recorded theme.", "observation_ids": [saved["id"]], "apparent_gaps": ["No workplace notes recorded."]}, self.root)
        text = Path(review["path"]).read_text()
        self.assertIn("not evidence of failure to perceive", text)

    def test_validation_rejects_bad_values(self):
        with self.assertRaises(ValueError):
            save_observation({"observation": "x", "brief": "y", "date": "bad", "evidence_status": "certain"}, self.root)
        with self.assertRaises(ValueError):
            get_observations_by_period("2026-10-01", "2026-09-01", self.root)

    def test_mcp_lists_four_tools(self):
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n"
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "vault_server.py")], input=request, text=True, capture_output=True, check=True)
        payload = json.loads(proc.stdout)
        self.assertEqual({tool["name"] for tool in payload["result"]["tools"]}, {"save_observation", "search_observations", "get_observations_by_period", "save_pattern_review"})


if __name__ == "__main__":
    unittest.main()
