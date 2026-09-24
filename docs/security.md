# Security and parity

This is a configuration merger, not a secrets importer or Hermes installer. It targets `~/.hermes` by default (or an explicit absolute `--home`), **previews without writing**, and only changes files with `--apply`. Existing YAML mappings are recursively merged: starter keys are updated, unrelated settings and secrets remain. Modified files are backed up to a unique mode-0600 `.backup[.N]` before replacement; new and merged files are written mode 0600. YAML formatting and comments are not preserved in merged files, so inspect backups and output. Invalid or duplicate YAML keys and incompatible mapping/scalar shapes abort before writes. A multi-file apply is not transactional on disk failure; restore backups manually if an error occurs mid-apply. Backups can contain secrets: keep them private and out of git. A pre-existing solver description is not modified, while solver config is merged and backed up. An existing project `.hermes.md` always blocks the optional policy install; merge it manually.

The renderer rejects symlink path components and YAML-special provider/model tokens. It is not a security sandbox and does not validate whether a chosen model is available. Inspect effective routing and authenticating provider after setup. A named profile can fall back to root-home credentials for the same provider; it is not an auth boundary. No `.env`, tokens, or personal state are shipped here.

## Approval policy

`delegation.subagent_auto_approve: false` auto-denies dangerous-command approval requests in unattended subagents; it does not prevent all side effects. The original local configuration used `true`; this starter intentionally differs. Change it only after evaluating the risk. Do not use `--yolo`, `--accept-hooks`, or broad approval modes merely for a demo.

## Publication

Project policy may not propagate into isolated Kanban workspaces: include critical constraints in a task body. A local-only card, commit, or passing test is not a published PR. Use a suitable completion contract for publication work and verify CI; see the upstream [Kanban reference](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban). No GitHub write is required by this starter.
