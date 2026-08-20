import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = REPOSITORY_ROOT / "hooks"


class AFSharpHookTests(unittest.TestCase):
    def run_hook(
        self, hook_name: str, payload: dict[str, object], home: Path
    ) -> dict[str, object]:
        temporary_directory = home / "tmp"
        temporary_directory.mkdir(exist_ok=True)

        env = os.environ.copy()
        env["HOME"] = str(home)
        env["TMPDIR"] = str(temporary_directory)
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        result = subprocess.run(
            [sys.executable, str(HOOKS_DIR / hook_name)],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(result.stdout) if result.stdout else {}

    @staticmethod
    def session_id(home: Path, suffix: str) -> str:
        return f"{home.name}-{suffix}"

    def test_fsharp_hook_handles_raw_patch_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            output = self.run_hook(
                "fsharp-reflex.py",
                {
                    "session_id": self.session_id(home, "raw-patch"),
                    "tool_name": "apply_patch",
                    "tool_input": (
                        "*** Begin Patch\n"
                        "*** Update File: src/Test.fs\n"
                        "@@\n"
                        "-old\n"
                        "+new\n"
                        "*** End Patch\n"
                    ),
                },
                home,
            )

        self.assertIn("fsharp-reflex", output["additionalContext"])
        self.assertEqual(
            output["additionalContext"],
            output["hookSpecificOutput"]["additionalContext"],
        )

    def test_fsharp_hook_handles_argument_shapes_and_safe_session_path(self) -> None:
        payloads = (
            {"toolInput": {"path": "Test.fs"}},
            {"tool_args": json.dumps({"file_path": "Test.fs"})},
            {"toolArgs": {"filePath": "Test.fs"}},
        )

        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            for index, arguments in enumerate(payloads):
                with self.subTest(arguments=arguments):
                    output = self.run_hook(
                        "fsharp-reflex.py",
                        {
                            "sessionId": f"../../{self.session_id(home, str(index))}",
                            "toolName": "create",
                            **arguments,
                        },
                        home,
                    )
                    self.assertIn("fsharp-reflex", output["additionalContext"])

            state_directory = home / ".copilot" / "state" / "fsharp-reflex"
            self.assertEqual(len(list(state_directory.glob("*.json"))), len(payloads))
            self.assertFalse((home.parent / f"{home.name}-0.json").exists())

    def test_fsharp_hook_preserves_delegation_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            session_id = self.session_id(home, "delegation")

            dispatch_output = self.run_hook(
                "fsharp-reflex.py",
                {
                    "session_id": session_id,
                    "tool_name": "task",
                    "tool_input": {"agent_type": "fsharp-coding"},
                },
                home,
            )
            first_edit_output = self.run_hook(
                "fsharp-reflex.py",
                {
                    "session_id": session_id,
                    "tool_name": "create",
                    "tool_input": {"path": "First.fs"},
                },
                home,
            )
            second_edit_output = self.run_hook(
                "fsharp-reflex.py",
                {
                    "session_id": session_id,
                    "tool_name": "create",
                    "tool_input": {"path": "Second.fs"},
                },
                home,
            )

        self.assertEqual(dispatch_output, {})
        self.assertEqual(first_edit_output, {})
        message = second_edit_output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("fsharp-validation", message)
        self.assertNotIn("delegate this edit", message)

    def test_fsharp_hook_registration_covers_supported_edit_tools(self) -> None:
        registration = json.loads(
            (HOOKS_DIR / "fsharp-reflex.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            set(registration["matchers"]["tool_name"]),
            {
                "edit",
                "create",
                "apply_patch",
                "bash",
                "powershell",
                "shell",
                "task",
                "skill",
            },
        )

    def test_fsharp_hook_handles_shell_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            for tool_name in ("bash", "powershell", "shell"):
                with self.subTest(tool_name=tool_name):
                    output = self.run_hook(
                        "fsharp-reflex.py",
                        {
                            "sessionId": self.session_id(home, tool_name),
                            "toolName": tool_name,
                            "toolInput": {"command": "printf x > Test.fs"},
                        },
                        home,
                    )
                    self.assertIn("fsharp-reflex", output["additionalContext"])


if __name__ == "__main__":
    unittest.main()
