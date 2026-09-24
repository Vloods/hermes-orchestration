# Troubleshooting

| Symptom | Check | Action |
| --- | --- | --- |
| `hermes` absent | `hermes --version` | Follow the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation); refresh PATH. |
| Python says `No module named yaml` | `.venv/bin/python -m pip show PyYAML` | Install `requirements.txt` into `.venv` and invoke the renderer with `.venv/bin/python`. |
| Model rejected / no credential | `hermes config get model` | Run `hermes setup`; choose model IDs your account actually supports. |
| Renderer refuses existing YAML | Read the error path and key | Fix invalid/duplicate YAML or incompatible mapping/scalar before applying; no files are written on preflight failure. |
| Renderer says `symlink` | Inspect target path and ancestors | Use a real directory, not an alias/symlink. |
| Existing solver differs | Inspect `profiles/solver/config.yaml` and `.backup` | The merger updates starter-owned solver keys, but leaves `profile.yaml` intact. Review before applying. |
| Project policy exists | Inspect project `.hermes.md` | Merge policy manually; the renderer will not replace it. |
| Card remains `ready` | `hermes gateway status`; `hermes kanban dispatch --dry-run` | Check gateway and assignee; don't install a second persistent service blindly. |
| Unexpected triage behavior | `hermes config get kanban` | Auto-decomposition is disabled in this starter; opt in deliberately. |
| Solver not picked | `hermes kanban show TASK_ID` | Explicitly assign `--assignee solver`; configuration alone does not route work. |
| Worker misses project rules | Inspect card workspace and body | Include essential constraints in the card; project rules may not propagate to isolated workspaces. |
| Task failed | `hermes kanban runs TASK_ID`; `hermes kanban show TASK_ID` | Examine run evidence, model and credential access; never infer completion from creation. |

For changes in newer Hermes versions, consult the [current docs](https://hermes-agent.nousresearch.com/docs) and `hermes <command> --help`.
