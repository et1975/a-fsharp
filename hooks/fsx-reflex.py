#!/usr/bin/env python3
"""PreToolUse audit hook: nag when a scriptable workflow bypasses fsx-orchestration.

Reads Copilot's hook JSON from stdin. Maintains a per-session ring buffer of
recent tool names under $TMPDIR. If the current tool would push a "scriptable"
tool's count over a threshold in the recent window — and no `.fsx` activity
has happened in that window — injects a one-line reminder via
hookSpecificOutput.additionalContext (non-blocking).

Failure mode: any error -> exit 0 silently. Audit, not a gate.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

# Tools that, when called repeatedly in a tight window, signal a fan-out /
# tree-walk / poll / filter shape that an `.fsx` would compress.
SCRIPTABLE_TOOLS = frozenset({
    "read_file",
    "grep_search",
    "file_search",
    "semantic_search",
    "fetch_webpage",
    "open_browser_page",
    "read_page",
})

TERMINAL_TOOL = "run_in_terminal"

TERMINAL_SCRIPTABLE_PATTERNS = (
    re.compile(r"\bfor\s+\w+\s+in\b"),
    re.compile(r"\bwhile\s*\["),
    re.compile(r"\bxargs\b"),
    re.compile(r"\|\s*head\b.*\|\s*tail\b"),
    re.compile(r";\s*sleep\s+\d"),
    # Inline interpreter one-liners: the primary pre-deliberation escape hatch
    re.compile(r"\bpython3?\s+-[ce]\b"),
    re.compile(r"\bperl\s+-[enwle]*e\b"),
    re.compile(r"\bnode\s+-[ep]\b"),
    re.compile(r"\bruby\s+-[rne]*e\b"),
)

FSX_SATISFY_PATTERN = re.compile(r"\.fsx\b|dotnet\s+fsi\b")

WINDOW = 6
THRESHOLD = 3
SAFE_SESSION = re.compile(r"[^A-Za-z0-9_.-]")


def buffer_path(session_id: str) -> Path:
    sid = SAFE_SESSION.sub("_", session_id or "default")[:64]
    return Path(tempfile.gettempdir()) / f"copilot-fsx-reflex-{sid}.log"


def load_recent(path: Path) -> list[str]:
    try:
        return path.read_text().splitlines()[-WINDOW:]
    except FileNotFoundError:
        return []
    except OSError:
        return []


def append(path: Path, entry: str) -> None:
    try:
        recent = load_recent(path)
        recent.append(entry)
        recent = recent[-WINDOW:]
        path.write_text("\n".join(recent) + "\n")
    except OSError:
        pass


def tool_signature(tool_name: str, tool_input: dict) -> str:
    """Encode tool call into a short line. Mark fsx-satisfying calls with !fsx."""
    sig = tool_name
    if tool_name == TERMINAL_TOOL:
        cmd = str(tool_input.get("command", ""))
        if FSX_SATISFY_PATTERN.search(cmd):
            sig = f"{tool_name}!fsx"
    elif tool_name == "create_file":
        path = str(tool_input.get("filePath", ""))
        if path.endswith(".fsx"):
            sig = f"{tool_name}!fsx"
    return sig


def is_terminal_scriptable(cmd: str) -> bool:
    return any(p.search(cmd) for p in TERMINAL_SCRIPTABLE_PATTERNS)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    session_id = str(payload.get("session_id", ""))
    if not tool_name:
        return 0

    path = buffer_path(session_id)
    recent = load_recent(path)

    satisfied = any("!fsx" in r for r in recent)

    sig = tool_signature(tool_name, tool_input)
    append(path, sig)

    if satisfied:
        return 0

    triggered_reason = None

    if tool_name in SCRIPTABLE_TOOLS:
        names_in_window = [r.split("!", 1)[0] for r in recent] + [tool_name]
        counts = Counter(n for n in names_in_window if n in SCRIPTABLE_TOOLS)
        top_tool, top_count = counts.most_common(1)[0]
        if top_count >= THRESHOLD:
            triggered_reason = (
                f"'{top_tool}' has been called {top_count} times in the last "
                f"{WINDOW} tool calls"
            )

    if not triggered_reason and tool_name == TERMINAL_TOOL:
        cmd = str(tool_input.get("command", ""))
        if is_terminal_scriptable(cmd):
            inline_match = re.search(r"\b(python3?|perl|node|ruby)\s+-\S*[ce]\b", cmd)
            if inline_match:
                triggered_reason = (
                    f"'{inline_match.group(0)}' is an inline-interpreter one-liner — "
                    "the exact pre-deliberation pattern fsx-orchestration exists to replace"
                )
            else:
                triggered_reason = "this terminal command looks like a loop/pipeline that an .fsx would express"

    if triggered_reason:
        msg = (
            f"[fsx-reflex] {triggered_reason}. Consider emitting one F# .fsx "
            "(fan-out / multi-tool / filter / poll / replay) instead of "
            "continuing the chain. Skill: ~/.copilot/skills/fsx-orchestration/. "
            "Shared library: ls ~/.copilot/scripts/ before authoring."
        )
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": msg,
                }
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
