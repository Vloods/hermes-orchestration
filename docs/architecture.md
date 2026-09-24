# Architecture

![Routing model](../assets/architecture.svg)

## Two different work lanes

`delegate_task` is a synchronous fork/join: a parent asks a bounded child for a result and resumes after it returns. The default agent stays the supervisor. Here `max_spawn_depth: 1` plus `orchestrator_enabled: false` makes delegated children leaves; `max_concurrent_children: 3` is a concurrency cap, **not** a promise that three jobs will start. Model/provider selection for delegation is separate from `model.default`.

Kanban is an asynchronous, persistent board shared across profiles. The CLI creates a card; the gateway-embedded dispatcher picks a ready card for a **named assigned profile**; a worker process reads the card using the `kanban_*` toolset and reports state. The board and its workspaces live under the chosen Hermes home. Tasks may be blocked, reviewed, reassigned, and retried. A card does not automatically import the caller's conversation transcript or its project-specific `.hermes.md` when it runs in an isolated workspace: include critical constraints in the card body, use a shared project workspace, or deliberately place the policy in the worker's workspace. Treat project worktrees and scratch workspaces differently; do not infer policy propagation from the parent's prompt.

A `solver` profile is independent configuration/state under `profiles/solver/`. It has a high-effort model but is **not** magically invoked when a task looks hard. Use an explicit `--assignee solver` card, or route through a real profile-aware mechanism. Profiles have separate config, skills, and memory; authentication is **not strictly isolated**: in the observed runtime, a named profile with no own provider credentials can fall back to the root `auth.json` for that provider (within the same Hermes home). Profile credentials take precedence. Board storage is also shared within a home. The starter does not clone or distribute credentials. Confirm solver access before allowing dispatch; do not treat a named profile as a credential security boundary.

## Control plane versus inference

`kanban.dispatch_in_gateway: true` means the gateway hosts the dispatcher; without an active gateway (or a deliberate manual dispatch command), ready tasks do not execute. The starter uses `auto_decompose: false` to avoid surprise auxiliary calls: opt in only after understanding the `triage` flow, configured profile descriptions, budget, and assignments. `orchestrator_profile` identifies who owns the root card **after** built-in decomposition, and `default_assignee` provides a routing fallback. Neither field swaps in a profile's prompt for the decomposer, whose model is `auxiliary.kanban_decomposer`. Empty strings retain upstream fallback behavior, not a solver default.

Local `agent.reasoning_effort` and auxiliary roles are explicit and may not be supported by every backend/model. Swap provider/model slots together and authenticate via upstream setup. No measured speedup/cost advantage is asserted by this architecture.

**Sources:** [Hermes Kanban reference](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban), [Hermes installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation), and [source snapshot](https://github.com/NousResearch/hermes-agent/commit/4a2bd7406ee3e09bd30a42cf9a7b970aac6edf9e). Check the current docs before making assumptions about later releases.
