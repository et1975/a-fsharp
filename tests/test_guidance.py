import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = (ROOT / "agents" / "fsharp-coding.agent.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "fsharp-validation" / "SKILL.md").read_text(encoding="utf-8")
INSTR = (ROOT / "copilot-instructions.md").read_text(encoding="utf-8")


class AgentGuidanceTests(unittest.TestCase):
    def test_precedence_section_ranks_local_precedent_over_defaults(self) -> None:
        self.assertIn("## Precedence", AGENT)
        self.assertLess(AGENT.index("Local precedent"), AGENT.index("This agent's defaults"))

    def test_phase1_requires_local_precedents_slot(self) -> None:
        self.assertIn("// Local precedents:", AGENT)
        self.assertIn("none found", AGENT)
        self.assertIn("New structure", AGENT)

    def test_self_review_checks_precedent_first(self) -> None:
        review = AGENT.split("#### Self-review before proceeding", 1)[1].split("### Phase 2", 1)[0]
        self.assertIn("0. ", review)
        self.assertIn("Local precedents", review)

    def test_corrections_section_present(self) -> None:
        self.assertIn("## Handling corrections", AGENT)

    def test_trivial_delta_keeps_precedent_slots(self) -> None:
        self.assertIn("still starts with the `Local precedents` and `New structure` header", AGENT)

    def test_defaults_gated_on_none_found(self) -> None:
        self.assertIn("greenfield defaults: use them for concerns whose `Local precedents` line says `none found`", AGENT)

    def test_correctness_rules_not_overridable(self) -> None:
        precedence = AGENT.split("## Precedence", 1)[1].split("## The Idiomatic F# Workflow", 1)[0]
        self.assertIn("Correctness rules", precedence)
        self.assertIn('`user: "', precedence)
        self.assertIn("the rest of the brief is parent wording", precedence)

    def test_report_recipe_and_fallback(self) -> None:
        self.assertIn("validation self-applied (no skill tool)", AGENT)
        for part in ("`Changes`", "`Local precedents`", "`New structure`", "`Conflicts`", "`Validation`"):
            self.assertIn(part, AGENT)

    def test_struct_du_escape_hatch_removed(self) -> None:
        self.assertNotIn("Unless an existing pattern dictates otherwise, prefer in order", AGENT)


class ValidationGuidanceTests(unittest.TestCase):
    def test_consistency_section_precedes_naming(self) -> None:
        self.assertIn("## Consistency with Neighbours", SKILL)
        self.assertLess(SKILL.index("## Consistency with Neighbours"), SKILL.index("## Naming Guidelines"))

    def test_correctness_tier_not_overridable(self) -> None:
        precedence = SKILL.split("## Precedence", 1)[1].split("## Consistency with Neighbours", 1)[0]
        self.assertIn("**Correctness rules**", precedence)
        self.assertIn("**Convention defaults**", precedence)
        self.assertIn('`user: "…"`', precedence)

    def test_new_structure_gate(self) -> None:
        self.assertIn("`New structure`", SKILL)

    def test_measure_case_rule_scoped_to_greenfield(self) -> None:
        row = next(l for l in SKILL.splitlines() if l.startswith("| UMX measure tag named"))
        self.assertIn("the project has no existing", row)

    def test_word_budget(self) -> None:
        self.assertLessEqual(len(SKILL.split()), 2500)


class InstructionGuidanceTests(unittest.TestCase):
    def test_delegation_brief_recipe_present(self) -> None:
        self.assertIn("### Delegation brief", INSTR)
        for slot in ("Goal", "Decisions", "Scope", "Context", "Acceptance", "Execution boundary"):
            self.assertIn(f"**{slot}**", INSTR)
        self.assertIn("draft — not user-approved", INSTR)
        self.assertIn('user: "', INSTR)
        self.assertIn('`user: "<quote>" → <observable check>`', INSTR)

    def test_validation_bullet_keeps_rerun_and_adds_consistency(self) -> None:
        self.assertIn("Fix every finding it reports and re-run it until clean.", INSTR)
        self.assertIn("*Consistency with Neighbours*", INSTR)
        self.assertIn("validation self-applied", INSTR)


if __name__ == "__main__":
    unittest.main()
