# Research grounding

Background and citations behind the `fsx-orchestration` skill. Not required reading — load only when justifying the pattern to a skeptic.

- Anthropic, *Code execution with MCP: Building more efficient agents* (Nov 4 2025) — measured **98.7% token reduction** (150k → 2k) on a Google Drive → Salesforce composition by code-orchestrating instead of streaming each intermediate value back through the model.
- Wang et al., *Executable Code Actions Elicit Better LLM Agents* (CodeAct, ICML 2024) — **+20% success rate** vs JSON tool calling.
- HuggingFace `smolagents` — `CodeAgent` vs `ToolCallingAgent`; code agents preferred for composability.
- Wang et al., *Voyager* (May 2023) — skill-library-of-code, **3.3–15.3× speedup** via reuse. Motivates the hybrid `./scripts/` (per-workspace) + `~/.copilot/scripts/` (shared) layout.
