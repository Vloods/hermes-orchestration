# Troubleshooting

| Symptom | Check | Action |
| --- | --- | --- |
| `hermes` absent | `hermes --version` | Follow the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation); refresh PATH. |
| Model rejected / no credential | `HERMES_HOME="$SANDBOX" hermes config get model` | Authenticate with `HERMES_HOME="$SANDBOX" hermes setup`; use available provider/model IDs and render a fresh home. Model names in this starter are not guaranteed entitlements. |
| Renderer says `existing destinations` | Read paths in stderr | Nothing was overwritten. Use a fresh home, or deliberately `--apply --backup-existing` only after reviewing the replacement risk. |
| Renderer says `symlink` | Inspect target path and ancestors | Use a real directory, not an alias/symlink; never work around the check by pointing at a live home inadvertently. |
| Card remains `ready` | `HERMES_HOME="$SANDBOX" hermes gateway status`; `... hermes kanban dispatch --dry-run` | Run the gateway in foreground for the sandbox. Do not install a host service just to test a throwaway home; an install may change a persistent user service. Confirm assignee exists. |
| Unexpected triage behavior | `... hermes config get kanban` | This starter disables auto-decomposition. Explicitly opt in and configure the auxiliary path/roles first. |
| Solver not picked | `... hermes kanban show TASK_ID` | Assign `--assignee solver` when creating the card; config alone does not route to solver. |
| Solver credential differs or fails | `HERMES_HOME="$SANDBOX" hermes --profile solver auth ...` (see `hermes auth --help`) | Profile auth may fall back to the sandbox root's provider credentials when absent; it is not strictly isolated. Check the selected provider/model and configure a profile-specific credential if required. |
| Worker misses project rules | Inspect task workspace and body | `.hermes.md` is workspace-local; include essential acceptance/security context in the card or place policy in the worker workspace. |
| Task failed or no result | `... hermes kanban runs TASK_ID`; `... hermes kanban show TASK_ID` | Examine run evidence and model/provider access; never infer completion from a card's creation. |

`$SANDBOX` above is a placeholder for your **absolute** Hermes home; `... hermes` means prefix the command with `HERMES_HOME="$SANDBOX"`. For changes in newer Hermes versions, use the [current docs](https://hermes-agent.nousresearch.com/docs) and `hermes <command> --help`.
