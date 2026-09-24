#!/usr/bin/env python3
"""Preview or apply a conservative Hermes configuration merge."""
import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]*$")
SLOTS = {"PROVIDER": "provider", "PRIMARY_MODEL": "primary_model", "DELEGATE_MODEL": "delegate_model",
         "AUX_MODEL": "aux_model", "SOLVER_MODEL": "solver_model"}
TEMPLATES = {"config.yaml": "config.yaml", "profiles/solver/config.yaml": "solver-config.yaml"}


class UniqueLoader(yaml.SafeLoader):
    """Refuse ambiguous mappings instead of silently dropping keys on a round trip."""


def construct_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"duplicate or non-string YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def parse_yaml(text, path):
    try:
        data = yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path} ({type(exc).__name__}); inspect locally") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"expected YAML mapping in {path}")
    return data


def merge(existing, desired, path=""):
    changed = []
    for key, value in desired.items():
        dotted = f"{path}.{key}" if path else key
        if key in existing and isinstance(value, dict):
            if not isinstance(existing[key], dict):
                raise ValueError(f"cannot merge mapping into non-mapping at {dotted}")
            changed.extend(merge(existing[key], value, dotted))
        elif key not in existing or existing[key] != value:
            existing[key] = value
            changed.append(dotted)
    return changed


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", type=Path, default=Path.home() / ".hermes", help="Hermes home (default: ~/.hermes)")
    p.add_argument("--project", type=Path, help="absolute project root for new project policy .hermes.md")
    p.add_argument("--provider", default="openai-codex")
    p.add_argument("--primary-model", default="gpt-6-astra")
    p.add_argument("--delegate-model", default="gpt-6-sol")
    p.add_argument("--aux-model", default="gpt-6-luna")
    p.add_argument("--solver-model", default="gpt-6-sol")
    p.add_argument("--apply", action="store_true", help="apply previewed changes (default: preview only)")
    return p


def reject_symlinks(path):
    for part in (path, *path.parents):
        if part == Path('/var') and os.path.realpath('/var') == '/private/var':
            continue  # macOS system alias
        if part.is_symlink():
            raise ValueError(f"symlink in target path: {part}")


def validate_path(path):
    if not path.is_absolute() or path == Path("/") or ".." in path.parts:
        raise ValueError("target paths must be absolute, normalized and not / or symlinks")
    reject_symlinks(path)
    if path.exists() and not path.is_dir():
        raise ValueError(f"target is not a directory: {path}")


def backup_path(dest):
    backup = dest.with_name(dest.name + ".backup")
    i = 1
    while backup.exists() or backup.is_symlink():
        backup = dest.with_name(dest.name + f".backup.{i}")
        i += 1
    return backup


def write_atomic(dest, text):
    fd, temp = tempfile.mkstemp(prefix=".hermes-starter-", dir=dest.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(text)
        os.chmod(temp, 0o600)
        os.replace(temp, dest)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def render(args):
    validate_path(args.home)
    if args.project:
        validate_path(args.project)
    values = {}
    for marker, attr in SLOTS.items():
        value = getattr(args, attr)
        if not TOKEN.fullmatch(value):
            raise ValueError(f"invalid {attr}: use a nonempty model/provider identifier (no YAML syntax)")
        values[marker] = value

    # Preflight ALL outputs before writing anything. Never display old config values.
    actions = []
    for rel, name in TEMPLATES.items():
        dest = args.home / rel
        reject_symlinks(dest)
        if dest.exists() and not dest.is_file():
            raise ValueError(f"destination is not a regular file: {dest}")
        text = (ROOT / "templates" / name).read_text(encoding="utf-8")
        for marker, value in values.items():
            text = text.replace("{{" + marker + "}}", value)
        if "{{" in text:
            raise ValueError(f"unresolved template marker in {name}")
        desired = parse_yaml(text, name)
        if dest.exists():
            existing = parse_yaml(dest.read_text(encoding="utf-8"), dest)
            keys = merge(existing, desired)
            output = yaml.safe_dump(existing, sort_keys=False, allow_unicode=True) if keys else None
        else:
            keys, output = list(desired), text
        actions.append((dest, output, keys))

    profile = args.home / "profiles/solver/profile.yaml"
    reject_symlinks(profile)
    if profile.exists() and not profile.is_file():
        raise ValueError(f"destination is not a regular file: {profile}")
    # A pre-existing named profile is user-owned: leave description and other metadata intact.
    actions.append((profile, None if profile.exists() else (ROOT / "templates/solver-profile.yaml").read_text(),
                    [] if profile.exists() else ["description", "description_auto"]))
    if args.project:
        policy = args.project / ".hermes.md"
        reject_symlinks(policy)
        if policy.exists():
            raise ValueError(f"project policy exists; install manually after reviewing: {policy}")
        actions.append((policy, (ROOT / "policy/.hermes.md").read_text(encoding="utf-8"), ["policy"]))

    for dest, output, keys in actions:
        if output is None:
            print(f"UNCHANGED: {dest}")
        else:
            verb = "MERGE" if dest.exists() else "CREATE"
            print(f"{'APPLY' if args.apply else 'PREVIEW'} {verb}: {dest} (keys: {', '.join(keys)})")
    if not args.apply:
        return
    for dest, output, _ in actions:
        if output is None:
            continue
        reject_symlinks(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if not dest.is_file():
                raise ValueError(f"destination changed during apply: {dest}")
            backup = backup_path(dest)
            fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as out, dest.open("rb") as source:
                shutil.copyfileobj(source, out)
            print(f"BACKUP: {backup}")
        write_atomic(dest, output)
        print(f"WROTE: {dest}")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        render(args)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
