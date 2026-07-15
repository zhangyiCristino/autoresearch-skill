import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "autoresearch"
EXPECTED_OPENAI_YAML = """interface:
  display_name: "ResearchHelm"
  short_description: "Scout, supervise, and audit bounded research"
  default_prompt: "Use $autoresearch in pi mode to turn my resources into decision-ready research options and audited experiments."
policy:
  allow_implicit_invocation: true
"""
CLAUDE_INSTALL_CONTRACT = (
    "/plugin marketplace add zhangyiCristino/autoresearch-skill",
    "/plugin install autoresearch@autoresearch-skill",
    "git clone https://github.com/zhangyiCristino/autoresearch-skill.git",
    "cp -r autoresearch-skill/skills/autoresearch ~/.claude/skills/",
)


class RepositoryContractTests(unittest.TestCase):
    def test_codex_metadata_is_exact_and_dependency_free(self):
        text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertEqual(EXPECTED_OPENAI_YAML, text)
        for forbidden in (
            "icon_small",
            "icon_large",
            "brand_color",
            "dependencies",
            "mcp",
            "credential",
        ):
            self.assertNotIn(forbidden, text.lower())

    def test_researchhelm_is_display_only_brand(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        market = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertTrue(
            english.startswith(
                "# ResearchHelm\n\n"
                "**Human-governed research, from resources to audited claims.**"
            )
        )
        self.assertTrue(
            chinese.startswith(
                "# ResearchHelm\n\n"
                "**人主导科研：从现有资源走向可审计结论。**"
            )
        )
        self.assertIn("\n# ResearchHelm\n", skill)
        self.assertIn("ResearchHelm", plugin["description"])
        self.assertIn("ResearchHelm", market["description"])
        self.assertIn("ResearchHelm", market["plugins"][0]["description"])
        self.assertNotIn("# Human-Governed Autoresearch", english + skill)

    def test_every_bundled_resource_is_referenced(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        referenced = set(
            re.findall(r"\((references/[^)]+|scripts/[^)]+)\)", skill)
        )
        for directory in ("references", "scripts"):
            for path in (SKILL_ROOT / directory).glob("*"):
                if path.is_file():
                    relative = path.relative_to(SKILL_ROOT).as_posix()
                    self.assertIn(relative, referenced, relative)

    def test_claude_identifiers_remain_exact(self):
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        market = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("autoresearch", plugin["name"])
        self.assertEqual("autoresearch-skill", market["name"])
        self.assertEqual(1, len(market["plugins"]))
        self.assertEqual("autoresearch", market["plugins"][0]["name"])
        self.assertEqual("./", market["plugins"][0]["source"])

    def test_claude_install_commands_and_paths_remain_exact(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for command in CLAUDE_INSTALL_CONTRACT:
            self.assertEqual(1, readme.count(command), command)
        self.assertEqual(1, readme.count("invoke `/autoresearch`"))


if __name__ == "__main__":
    unittest.main()
