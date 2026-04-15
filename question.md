The question:

> **Should coding guidance be captured as an *agent* or as a *skill/tool*?**

is really shorthand for a deeper control‑plane design problem:

> Is coding policy **reasoning‑time behavior** or **execution‑time capability**?

Below is the current **state‑of‑the‑art mental model (2025–2026)** that’s emerging across internal Copilot stack designs, SWE‑Agent literature, and production agentic platforms.

***

# 1. First: What are you actually trying to capture?

Coding guidance is usually one of these:

| Guidance Type             | Example                            | Nature               |
| ------------------------- | ---------------------------------- | -------------------- |
| Architectural conventions | "Functions must be idempotent"       | reasoning constraint |
| Security policy           | "No secrets in plain text"         | validation rule      |
| Platform usage            | "Use internal PS SDK wrapper"      | tool selection       |
| Process policy            | "Create DRIs for breaking changes" | workflow logic       |
| Code patterns             | Retry semantics, logging shape     | generation bias      |
| Runtime safety            | "No ARM PUT loops"                 | execution constraint |

Now the key insight:

👉 **Some of these must influence planning**  
👉 **Some must gate execution**

And those become **two completely different architectural problems**

This is where the *Agent vs Skill* split shows up.

***

# 2. Coding Guidance as a Skill (Tool / Function)

### Model:

You encode guidance as:

    lint()
    validate()
    secure_string_enforcer()
    _Function_policy_check()
    idempotency_detector()

Then the agent:

    reason → generate code → call guidance skill → observe result → iterate

### Pros ✅

### ✔ Deterministic + auditable

You get:

    plan
    call skill
    constraint check
    retry

instead of:

    🤞 model remembers to follow rule in prompt

This matters massively for:

*   compliance
*   security posture
*   reproducibility
*   pipeline use
*   regulated infra

***

### ✔ Enables separation of:

| concern                 | location  |
| ----------------------- | --------- |
| Generation intelligence | Agent     |
| Correctness policy      | Skill     |
| Enforcement             | Runtime   |
| Governance              | Org layer |

Which maps cleanly to:

    prompt ≠ policy

(one of the biggest current industry corrections btw)

***

### ✔ Works with smaller planning models

Planner LLM becomes orchestration brain:

    observe → decide → call validator skill

You no longer require:

> "GPT‑5 must know internal Microsoft PS SDK logging contract"

***

### Cons ❌

*   Guidance applied **after** reasoning
*   Not guaranteed to shape architecture
*   Can produce:

<!---->

    generate bad pattern
    repair bad pattern
    repair repair repair

aka:

> reactive correctness instead of proactive correctness

You’ll see:

*   retry loops
*   tool‑use inflation
*   latency creep
*   guidance drift under exploration

***

# 3. Coding Guidance as an Agent

Here guidance becomes:

    ModuleAuthoringAgent
    SecurityEnforcementAgent
    PipelinePolicyAgent
    AzureLinuxPortingAgent

Each one is:

    goal-conditioned reasoning policy

They don't check output.

They shape:

✅ planning  
✅ architectural decision making  
✅ implementation strategy  
✅ decomposition

before generation ever happens.

***

### Pros ✅

### ✔ Planning‑time influence

This is the *big one.*

The model now plans like:

    I must ensure idempotency
    → avoid PUT loops
    → use GET-diff-apply pattern
    → create converge step

Instead of:

    generate PUT loop
    validator screams
    rewrite with converge logic

***

### ✔ Domain reasoning specialization

Exactly why:

*   SWE-Agent
*   Devin-like architectures
*   CodeAct
*   CrewAI roles
*   AutoGen team agents

are role‑based now instead of prompt‑stacking.

***

### ✔ Composability via debate/critique loops

You get patterns like:

    AuthoringAgent → SecurityAgent → ReliabilityAgent → ApproverAgent

Guidance becomes:

> emergent from multi-agent negotiation

instead of:

> embedded in a static prompt blob

***

### Cons ❌

*   Probabilistic compliance
*   Prompt drift
*   Harder auditability
*   Requires memory or persistent state
*   Organizational policy becomes stochastic 🙃

(Security teams *hate* this unless paired with enforcement layer)

***

# 4. Industry Consensus (2026)

No serious production agent platform today treats coding guidance as:

✅ purely agent  
or  
✅ purely skill

Instead the convergence architecture is:

# 👉 **Agentic Planning + Skill-Based Governance**

AKA:

    Reason with agents
    Enforce with tools

***

### The now‑canonical layering looks like:

                    ┌────────────────────────────┐
                    │   Planning Agents           │
                    │                            │
                    │  - Function Authoring Agent  │
    User Goal  →    │  - Security Aware Agent    │
                    │  -  Platform Agent      │
                    └────────────┬───────────────┘
                                 ↓
                    ┌────────────────────────────┐
                    │  Guidance Skills (Hard)    │
                    │                            │
                    │  - Secret Analyzer         │
                    │  - ARM Safety Validator    │
                    │  - Idempotency Checker     │
                    │  - SDK Usage Enforcer      │
                    └────────────┬───────────────┘
                                 ↓
                    Execution / CI Gate

***

Which conceptually becomes:

| Layer             | Concern | Representation |
| ----------------- | ------- | -------------- |
| Intent planning   | Agent   |                |
| Domain heuristics | Agent   |                |
| Code style bias   | Agent   |                |
| Correctness       | Skill   |                |
| Security policy   | Skill   |                |
| Compliance        | Skill   |                |
| Release gate      | Skill   |                |

***

# 5. The Emerging Design Principle

### ✅ Use agents for:

*   *How should I do this?*
*   planning
*   decomposition
*   architecture
*   workflow ordering
*   tradeoffs
*   platform strategy

***

### ✅ Use skills for:

*   *Is this allowed?*
*   invariants
*   security
*   policy enforcement
*   SDK requirements
*   runtime safety
*   naming conventions
*   forbidden patterns
*   compliance
*   formal org mandates

***

# 6. The Rule of Thumb Teams Are Settling On

If violating the rule should:

| Consequence        | Put Guidance In |
| ------------------ | --------------- |
| Increase latency   | Agent           |
| Produce bugs       | Agent           |
| Leak secrets       | Skill           |
| Break infra        | Skill           |
| Violate compliance | Skill           |
| Cause outage       | Skill           |
| Look ugly          | Agent           |

***


# 9. One‑Sentence State‑of‑the‑Art Summary

> Planning‑level coding guidance belongs in **agents**.  
> Policy‑level coding guidance belongs in **skills**.

***
