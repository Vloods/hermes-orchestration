![Hermes Orchestration](assets/banner.svg)

# Hermes Orchestration

[![Starter checks](https://github.com/Vloods/hermes-orchestration/actions/workflows/check.yml/badge.svg)](https://github.com/Vloods/hermes-orchestration/actions/workflows/check.yml)

**Give every agent a clear job—and keep the final decision with you.** A small, inspectable starter for Hermes Agent: one supervisor, short-lived delegates, a durable Kanban lane for named specialists, and auxiliary work on its own model lane. Configuration and project policy, not a new runtime.

[Setup](docs/setup.md) · [Architecture](docs/architecture.md) · [Security](docs/security.md) · [Русский](README.ru.md)

![Two work lanes and auxiliary services](assets/architecture.svg)

## Start here

**Already use Hermes?** [Merge into your existing installation](docs/setup.md#route-a--hermes-already-installed): preview the changed keys, then explicitly apply. Unrelated YAML settings remain; modified files are backed up. Your existing named `solver` profile description is left alone.

**Installing Hermes now?** [Follow the fresh-install route](docs/setup.md#route-b--fresh-hermes-installation). The normal target is `~/.hermes`, not a special sandbox. Authenticate with upstream `hermes setup`.

Both routes use a local Python virtual environment with [PyYAML](requirements.txt). A quick preview from the cloned repo:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/render.py              # preview only; default ~/.hermes
# Review keys and model availability, then repeat with --apply and your model flags.
```

The illustrative `astra` / `sol` / `luna` model IDs are **not guaranteed available**. Set `--provider`, `--primary-model`, `--delegate-model`, `--aux-model`, and `--solver-model` to models your account supports; preview and apply with identical flags. A named `solver` is not automatically chosen for hard work—assign it deliberately on the board. No paid model call is part of installation or tests.

## Learn and adapt

- [Setup and operation](docs/setup.md) — merge semantics, installation, project policy, and the board.
- [Architecture](docs/architecture.md) — supervisor, delegates, Kanban and auxiliary routing.
- [Security](docs/security.md) · [Troubleshooting](docs/troubleshooting.md) · [Russian guide](docs/guide.ru.md).
- [Compact project policy](policy/.hermes.md) · [full original policy reference](policy/reference.hermes.md). Configuration is not policy.

## Community

Questions and suggestions belong in [GitHub Issues](https://github.com/Vloods/hermes-orchestration/issues). This is a community project, **not affiliated with or endorsed by Nous Research**; consult the [current Hermes documentation](https://hermes-agent.nousresearch.com/docs) for upstream behavior.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes, offline tests, and safety expectations.

## License

[MIT](LICENSE) covers this repository's original material, not upstream Hermes Agent.

## Citation

If this starter informs your work, cite it using [CITATION.cff](CITATION.cff). No DOI is claimed.
