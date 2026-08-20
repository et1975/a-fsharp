#!/usr/bin/env python3
"""PreToolUse audit hook: nag when F# edits skip `fsharp-coding` delegation or `fsharp-validation`.

Reads Copilot's hook JSON from stdin. Per-session state under
~/.copilot/state/fsharp-reflex/<session>.json keeps reminders to once per phase.

Failure mode: any error -> exit 0 silently. Audit, not a gate.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

FS_EXTS = (".fs", ".fsi", ".fsx", ".fsproj")
AGENT_NAME = "fsharp-coding"
SKILL_NAME = "fsharp-validation"

STATE_DIR = Path.home() / ".copilot" / "state" / "fsharp-reflex"
SAFE_SESSION = re.compile(r"[^A-Za-z0-9_.-]")

TOOL_NAME_ALIASES = {
    "Edit": "edit",
    "Write": "create",
    "Create": "create",
    "ApplyPatch": "apply_patch",
    "Bash": "bash",
    "powershell": "bash",
    "shell": "bash",
    "Task": "task",
    "Skill": "skill",
}


def read_event() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def read_tool_input(event: dict[str, Any]) -> Any:
    value = next(
        (
            event.get(key)
            for key in ("tool_input", "toolInput", "tool_args", "toolArgs")
            if event.get(key) is not None
        ),
        {},
    )
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else value
        except json.JSONDecodeError:
            return value
    return {}


def emit(message: str | None) -> None:
    if not message:
        sys.exit(0)
    payload = {
        "additionalContext": message,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message,
        }
    }
    json.dump(payload, sys.stdout)
    sys.exit(0)


def state_path(session_id: str) -> Path:
    safe_id = SAFE_SESSION.sub("_", session_id or "default")[:64]
    return STATE_DIR / f"{safe_id}.json"


def load_state(session_id: str) -> dict[str, Any]:
    if not session_id:
        return {}
    path = state_path(session_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(session_id: str, state: dict[str, Any]) -> None:
    if not session_id:
        return
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = state_path(session_id)
    try:
        path.write_text(json.dumps(state))
    except OSError:
        pass


def is_fsharp_path(path: str | None) -> bool:
    if not path:
        return False
    return path.lower().endswith(FS_EXTS)


def fsharp_path_in_bash(command: str | None) -> bool:
    """Detect heredoc/redirect writes into an F# file from a bash command."""
    if not command:
        return False
    pat = re.compile(
        r"(?:>>?|tee(?:\s+-a)?\s+)\s*['\"]?[^\s'\"<>|;&]+\.(?:fs|fsi|fsx|fsproj)\b",
        re.IGNORECASE,
    )
    return bool(pat.search(command))


def fsharp_path_in_patch(tool_input: Any) -> bool:
    if isinstance(tool_input, str):
        patch = tool_input
    elif isinstance(tool_input, dict):
        patch = next(
            (
                value
                for key in ("patch", "input", "arguments")
                if isinstance((value := tool_input.get(key)), str)
            ),
            "",
        )
    else:
        return False

    header = re.compile(
        r"^\*\*\* (?:Add|Update|Delete) File: .+\.(?:fs|fsi|fsx|fsproj)\s*$"
        r"|^\*\*\* Move to: .+\.(?:fs|fsi|fsx|fsproj)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(header.search(patch))


def target_is_fsharp(tool_name: str, tool_input: Any) -> bool:
    if tool_name == "apply_patch":
        return fsharp_path_in_patch(tool_input)
    if not isinstance(tool_input, dict):
        return False
    if tool_name in {"edit", "create"}:
        path = next(
            (
                tool_input.get(key)
                for key in ("path", "file_path", "filePath")
                if tool_input.get(key) is not None
            ),
            None,
        )
        return is_fsharp_path(path)
    if tool_name == "bash":
        return fsharp_path_in_bash(tool_input.get("command"))
    return False


def main() -> None:
    event = read_event()

    tool_name = (
        event.get("tool_name")
        or event.get("toolName")
        or os.environ.get("COPILOT_TOOL_NAME", "")
    )
    tool_name = TOOL_NAME_ALIASES.get(tool_name, tool_name)
    tool_input = read_tool_input(event)
    session_id = (
        event.get("session_id")
        or event.get("sessionId")
        or os.environ.get("COPILOT_SESSION_ID", "")
    )
    agent_name = (
        event.get("agent_name")
        or event.get("agentName")
        or os.environ.get("COPILOT_AGENT_NAME", "")
    )

    # Recursion guard: when fsharp-coding itself is editing F# files,
    # the agent IS the delegation target. Stay silent.
    if agent_name == AGENT_NAME:
        emit(None)

    state = load_state(session_id)
    state.setdefault("agent_dispatched", False)
    state.setdefault("validation_since_last_edit", True)
    state.setdefault("pending_edits", 0)

    reminder: str | None = None

    # Track positive signals before evaluating edits, so a delegated/validated
    # call in the same turn isn't punished.
    if tool_name == "task" and isinstance(tool_input, dict):
        agent_type = tool_input.get("agent_type") or tool_input.get("subagent_type")
        if agent_type == AGENT_NAME:
            state["agent_dispatched"] = True

    elif tool_name == "skill" and isinstance(tool_input, dict):
        if tool_input.get("skill") == SKILL_NAME:
            state["validation_since_last_edit"] = True
            state["pending_edits"] = 0

    elif target_is_fsharp(tool_name, tool_input):
        missing: list[str] = []
        if not state["agent_dispatched"]:
            missing.append(
                f"delegate this edit to the `{AGENT_NAME}` agent via the `task` tool"
            )
        if not state["validation_since_last_edit"]:
            missing.append(
                f"invoke the `{SKILL_NAME}` skill on the previous F# edit before "
                f"making another one"
            )
        if missing:
            reminder = (
                "fsharp-reflex: about to touch an F# file — "
                + "; ".join(missing)
                + "."
            )
        state["validation_since_last_edit"] = False
        state["pending_edits"] += 1

    save_state(session_id, state)
    emit(reminder)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Hooks must never break the agent. Fail open.
        sys.exit(0)
