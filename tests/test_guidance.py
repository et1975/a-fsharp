import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = (ROOT / "agents" / "fsharp-coding.agent.md").read_text(encoding="utf-8")
SKILL = (ROOT / "skills" / "fsharp-validation" / "SKILL.md").read_text(encoding="utf-8")
INSTR = (ROOT / "copilot-instructions.md").read_text(encoding="utf-8")
GUIDANCE = (AGENT, SKILL, INSTR)


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


class AgentGuidanceTests(unittest.TestCase):
    def test_precedence_section_ranks_local_precedent_over_defaults(self) -> None:
        self.assertIn("## Precedence", AGENT)
        self.assertLess(AGENT.index("Local precedent"), AGENT.index("This agent's defaults"))

    def test_phase1_surveys_precedent_before_modelling(self) -> None:
        phase1 = section(AGENT, "### Phase 1", "#### Module boundary rules")
        self.assertLess(phase1.index("Survey local precedent"), phase1.index("Produce the model artifact"))

    def test_model_artifact_does_not_record_precedents(self) -> None:
        phase1 = section(AGENT, "### Phase 1", "#### Module boundary rules")
        self.assertNotIn("// Local precedents", phase1)
        self.assertNotIn("New structure", phase1)

    def test_self_review_checks_precedent_first(self) -> None:
        review = section(AGENT, "#### Self-review before proceeding", "### Phase 2")
        self.assertIn("0. New code mirrors or extends the precedent found in Step 1", review)

    def test_corrections_section_present(self) -> None:
        self.assertIn("## Handling corrections", AGENT)

    def test_defaults_gated_on_survey(self) -> None:
        self.assertIn("Every representation choice in this file outside the correctness rules is a greenfield default", AGENT)
        self.assertIn("Use them only for concerns where the Step 1 survey found no precedent.", AGENT)

    def test_later_representation_directives_defer_to_precedent(self) -> None:
        self.assertIn("**Domain errors** → the failure idiom found in Step 1", AGENT)
        self.assertIn("report failure with the project's idiom", AGENT)
        self.assertIn("mirror existing companions (greenfield default: `create`/`value`)", AGENT)
        self.assertNotIn("**Domain errors** → `Result<'T, DomainError>`.", AGENT)
        self.assertNotIn("never throw, return Result.", AGENT)

    def test_correctness_rules_not_overridable(self) -> None:
        precedence = section(AGENT, "## Precedence", "## The Idiomatic F# Workflow")
        self.assertIn("Correctness rules", precedence)
        self.assertIn("attributes them to the user", precedence)

    def test_report_recipe(self) -> None:
        report = section(AGENT, "**Report**", "## Handling corrections")
        for part in ("`Changes`", "`Local precedents`", "`New structure`", "`Conflicts`", "`Validation`"):
            self.assertIn(part, report)

    def test_skill_tool_in_frontmatter(self) -> None:
        frontmatter = AGENT.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^\s*-\s*skill\s*$")

    def test_struct_du_escape_hatch_removed(self) -> None:
        self.assertNotIn("Unless an existing pattern dictates otherwise, prefer in order", AGENT)


class ValidationGuidanceTests(unittest.TestCase):
    def test_consistency_section_precedes_naming(self) -> None:
        self.assertIn("## Consistency with Neighbours", SKILL)
        self.assertLess(SKILL.index("## Consistency with Neighbours"), SKILL.index("## Naming Guidelines"))

    def test_correctness_tier_not_overridable(self) -> None:
        precedence = section(SKILL, "## Precedence", "## Consistency with Neighbours")
        self.assertIn("**Correctness rules**", precedence)
        self.assertIn("**Convention defaults**", precedence)
        self.assertIn("attributes that approval to the user", precedence)

    def test_justified_new_structure_gate(self) -> None:
        self.assertIn("states why this item could not reuse or extend the existing one", SKILL)

    def test_measure_case_rule_scoped_to_greenfield(self) -> None:
        row = next(l for l in SKILL.splitlines() if l.startswith("| UMX measure tag named"))
        self.assertIn("the project has no existing", row)

    def test_measure_casing_consistency_row(self) -> None:
        self.assertIn("| `[<Measure>]` whose casing differs from existing measures |", SKILL)

    def test_word_budget(self) -> None:
        self.assertLessEqual(len(SKILL.split()), 2500)


class InstructionGuidanceTests(unittest.TestCase):
    def test_delegation_brief_recipe_present(self) -> None:
        self.assertIn("### Delegation brief", INSTR)
        for slot in ("Goal", "Decisions", "Scope", "Context", "Acceptance", "Execution boundary"):
            self.assertIn(f"**{slot}**", INSTR)
        self.assertIn("in the user's words and attributed to them", INSTR)

    def test_validation_bullet_keeps_rerun_and_adds_consistency(self) -> None:
        self.assertIn("Fix every finding it reports and re-run it until clean.", INSTR)
        self.assertIn("*Consistency with Neighbours*", INSTR)


class SchemaNeutralityTests(unittest.TestCase):
    def test_no_fixed_provenance_syntax(self) -> None:
        for text in GUIDANCE:
            self.assertNotIn('user: "', text)
            self.assertNotIn("draft — not user-approved", text)

    def test_no_self_applied_fallback(self) -> None:
        for text in GUIDANCE:
            self.assertNotIn("self-applied", text)

    def test_no_local_install_paths_in_new_guidance(self) -> None:
        self.assertIsNone(re.search(r"~/\.copilot/skills/fsharp-validation", AGENT))


if __name__ == "__main__":
    unittest.main()
