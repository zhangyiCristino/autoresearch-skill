import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "evals" / "shared" / "scenarios.json"

REQUIRED_IDS = {
    "resource-driven-ideation", "premature-novelty", "infeasible-idea",
    "skipped-gate", "unauthorized-scope-growth", "lucky-seed-selection",
    "anomalous-gain", "resume-drift", "untraceable-figure",
    "metric-only-win", "partial-skill-download", "missing-shell-or-git",
    "offline-public-search", "pi-mode-vs-pi-client", "installer-is-not-native",
    "portable-gate-silence", "irrelevant-skill-spam", "installed-skill-first",
    "stars-are-not-trust", "fabricated-skill-provenance",
    "malicious-skill-gate-bypass", "no-auto-install", "skill-hash-drift",
    "too-many-skill-candidates", "untrusted-readme-command", "skill-permission-expansion",
    "recommendation-cycle", "repeat-rejected-skill", "private-query-leak",
    "read-agent-auth-files", "dump-environment", "credential-in-command",
    "authorization-log", "upload-private-cockpit", "commit-local-identity",
    "recommended-skill-requests-credentials", "allowlist-real-token",
    "publish-after-security-failure",
}

PORTABLE_REQUIRED_IDS = {
    "partial-skill-download",
    "missing-shell-or-git",
    "offline-public-search",
    "portable-gate-silence",
    "no-auto-install",
    "malicious-skill-gate-bypass",
}


class EvalContractTests(unittest.TestCase):
    def test_shared_scenarios_are_complete_and_unique(self):
        payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        records = payload["scenarios"]
        ids = [record["id"] for record in records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), REQUIRED_IDS)
        for record in records:
            self.assertIn(record["category"], {"core", "portable", "recommendation", "security"})
            self.assertTrue(record["prompt"].strip())
            self.assertGreaterEqual(len(record["pass_contract"]), 2)
            self.assertIsInstance(record["key_wording"], bool)
            self.assertIsInstance(record["required_capabilities"], list)

    def test_adapters_reference_only_shared_scenarios(self):
        payload = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        records = payload["scenarios"]
        ids = {record["id"] for record in records}
        core_security_ids = {
            record["id"]
            for record in records
            if record["category"] in {"core", "security"}
        }
        portable_security_ids = {
            record["id"]
            for record in records
            if record["category"] == "security"
            and set(record["required_capabilities"]).issubset({"files", "shell", "git"})
        }
        expected_ids = {
            "claude": core_security_ids,
            "codex": ids,
            "portable": PORTABLE_REQUIRED_IDS | portable_security_ids,
        }
        for runtime in ("claude", "codex", "portable"):
            path = ROOT / "evals" / runtime / "adapter.json"
            adapter = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(adapter["runtime"], runtime)
            self.assertEqual(len(adapter["scenario_ids"]), len(set(adapter["scenario_ids"])))
            self.assertEqual(set(adapter["scenario_ids"]), expected_ids[runtime])
            self.assertTrue(adapter["fresh_context"])
            self.assertEqual(adapter["evidence_directory"], f"evals/results/{runtime}")
            if runtime == "claude":
                self.assertEqual(
                    adapter["legacy_case_ids"],
                    ["equal-metric-tie", "eval-peek-refusal"],
                )
                self.assertTrue(set(adapter["legacy_case_ids"]).isdisjoint(ids))


if __name__ == "__main__":
    unittest.main()
