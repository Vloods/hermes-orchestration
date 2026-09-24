# Contributing

Issues and focused pull requests are welcome at [Vloods/hermes-orchestration](https://github.com/Vloods/hermes-orchestration/issues). Describe the behavior, expected result, affected Hermes version, and a safe reproduction without credentials or personal paths. No Discussions forum is currently enabled.

1. Fork and create a branch; keep changes scoped and preserve the full reference policy at `policy/reference.hermes.md` unless explicitly revising that historical reference.
2. Install the renderer dependency in a local virtual environment: `python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`.
3. Run `.venv/bin/python -m unittest discover -s tests -v`. Tests must use fixture homes; never operate on your real `~/.hermes`, create paid model calls, or add secrets.
4. When changing templates or merge behavior, add positive and negative fixtures (existing config, solver profile, backups, preview, invalid YAML). Review doc links and rendered SVG previews for visual changes.
5. Explain what changed and which checks passed in the PR. Do not claim upstream compatibility beyond the runtime you tested; distinguish configuration from project policy and illustrative model IDs from available entitlements.

This community repository is independent of Nous Research. Respect upstream Hermes Agent licensing and documentation.
