# Setup and operation

This repository adds **configuration and project policy**, not a new Hermes runtime. Use a virtual environment for the renderer's sole dependency:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run commands from the cloned repository. The default target is the ordinary `~/.hermes` home. **Preview first** (no writes); inspect the paths and changed key names before applying. You can choose an alternate absolute home with `--home /absolute/path` for testing, but no sandbox is required for normal use.

## Route A — Hermes already installed

1. Check `hermes --version`, your existing `~/.hermes/config.yaml`, and whether `~/.hermes/profiles/solver` is already in use. Pick provider/model IDs that your account supports. The four model slots shown below are illustrative, not guaranteed entitlements.
2. Preview and apply explicitly:

   ```bash
   .venv/bin/python scripts/render.py --provider YOUR_PROVIDER --primary-model YOUR_PRIMARY --delegate-model YOUR_DELEGATE --aux-model YOUR_AUX --solver-model YOUR_SOLVER
   .venv/bin/python scripts/render.py --provider YOUR_PROVIDER --primary-model YOUR_PRIMARY --delegate-model YOUR_DELEGATE --aux-model YOUR_AUX --solver-model YOUR_SOLVER --apply
   hermes profile list
   hermes config get model
   ```

   Repeat the *same* flags for preview and apply. Existing YAML mappings are merged recursively: only starter-owned keys are set, unrelated keys (including plugin, gateway, provider and secret fields) remain. Modified files get mode-0600 `.backup`, `.backup.1`, etc. **This is a semantic YAML merge, not a formatting/comment-preserving editor**: inspect the backup and resulting config. Existing `solver/profile.yaml` is never overwritten; existing `solver/config.yaml` is merged and backed up, so review its model/reasoning changes before applying. Invalid/ambiguous YAML or a conflicting scalar blocks the whole preflight. A multi-file apply is not transactional if disk or permissions fail mid-write; restore from backups if necessary. Do not apply blindly to a heavily customized solver profile.
3. The renderer does not manage credentials. Inspect resulting effective settings and authenticate through the official `hermes setup` or `hermes --profile solver auth ...` if needed. Named profile credentials may fall back to root credentials for the same provider; the profile is not an auth boundary.

## Route B — Fresh Hermes installation

1. Follow the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation) for your platform; on supported macOS/Linux/WSL2 CLI installations the upstream command is `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash` (review network-sourced scripts first). Check `hermes --version`.
2. Clone with `git clone https://github.com/Vloods/hermes-orchestration.git && cd hermes-orchestration`, install the Python dependency above, and run `.venv/bin/python scripts/render.py` (first preview, then repeat with `--apply`). On a fresh home, the renderer creates the minimal default and solver YAML and solver metadata. Change model flags if your provider lacks the illustrative defaults.
3. Run `hermes setup` to choose a provider and authenticate. Setup may edit config: inspect your effective model/provider afterwards, and re-preview only if you intend to reapply starter keys. No tokens or auth files come from this repository.

## Optional project policy

`policy/.hermes.md` is the compact project-local policy; `policy/reference.hermes.md` preserves the full original orchestration policy. To preview creation of a policy in a **new** project, pass `--project /absolute/path/to/project` with the same renderer flags before `--apply`. If `.hermes.md` already exists, the renderer refuses the whole operation; review and merge policy manually instead. It does not install a global policy, and project rules do not automatically propagate to isolated Kanban workspaces.

## Board and gateway

After authentication, check whether a gateway service already exists before starting another one (`hermes gateway status`). For a fresh foreground gateway, run `hermes kanban init`, then `hermes gateway run` in a separate terminal. `hermes kanban dispatch --dry-run` checks readiness without spawning a worker. The starter has `kanban.auto_decompose: false`; no automatic solver assignment is configured. To send a card to the named solver, explicitly use `--assignee solver`:

```bash
hermes kanban create "Inspect a bounded task" --assignee solver --body "Return evidence and limitations; do not edit files." --completion-contract local-only
hermes kanban show TASK_ID
hermes kanban runs TASK_ID
```

**Creating a ready card may trigger a paid model call.** Do not run this example until models and auth are working. A card's creation is not completion. For persistent service installation, inspect the installed Hermes gateway service and existing host service first. Review [architecture](architecture.md), [security](security.md), and [troubleshooting](troubleshooting.md) for operational details. Tests are offline and never create a card or touch the live home.
