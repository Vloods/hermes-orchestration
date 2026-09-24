#!/usr/bin/env python3
"""Render a minimal Hermes starter into an explicitly chosen home (stdlib only)."""
import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]*$")
SLOTS = {
    "PROVIDER": "provider", "PRIMARY_MODEL": "primary_model",
    "DELEGATE_MODEL": "delegate_model", "AUX_MODEL": "aux_model",
    "SOLVER_MODEL": "solver_model",
}
TEMPLATES = {
    "config.yaml": "config.yaml",
    "profiles/solver/config.yaml": "solver-config.yaml",
    "profiles/solver/profile.yaml": "solver-profile.yaml",
}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", type=Path, required=True, help="absolute target Hermes home; never inferred")
    p.add_argument("--project", type=Path, help="absolute project root for policy .hermes.md")
    p.add_argument("--provider", default="openai-codex")
    p.add_argument("--primary-model", default="gpt-6-astra")
    p.add_argument("--delegate-model", default="gpt-6-sol")
    p.add_argument("--aux-model", default="gpt-6-luna")
    p.add_argument("--solver-model", default="gpt-6-sol")
    p.add_argument("--apply", action="store_true", help="write files (default: dry-run)")
    p.add_argument("--backup-existing", action="store_true", help="opt in to replace existing files after backing them up")
    return p


def reject_symlinks(path):
    for part in (path, *path.parents):
        # macOS supplies /var as a system alias to /private/var; mktemp uses it.
        if part == Path('/var') and os.path.realpath('/var') == '/private/var':
            continue
        if part.is_symlink():
            raise ValueError(f"symlink in target path: {part}")


def validate_path(path):
    if not path.is_absolute() or path == Path("/"):
        raise ValueError("target paths must be absolute and not / or symlinks")
    reject_symlinks(path)
    if path.exists() and not path.is_dir():
        raise ValueError(f"target is not a directory: {path}")


def render(args):
    validate_path(args.home)
    if args.project:
        validate_path(args.project)
    if args.backup_existing and not args.apply:
        raise ValueError("--backup-existing requires --apply")
    values = {}
    for marker, attr in SLOTS.items():
        value = getattr(args, attr)
        if not TOKEN.fullmatch(value):
            raise ValueError(f"invalid {attr}: use a nonempty model/provider identifier (no YAML syntax)")
        values[marker] = value
    files = {}
    for dest, name in TEMPLATES.items():
        text = (ROOT / "templates" / name).read_text(encoding="utf-8")
        for marker, value in values.items():
            text = text.replace("{{" + marker + "}}", value)
        if "{{" in text:
            raise ValueError(f"unresolved template marker in {name}")
        files[args.home / dest] = text
    if args.project:
        files[args.project / ".hermes.md"] = (ROOT / "policy" / ".hermes.md").read_text(encoding="utf-8")
    # Validate every destination before changing anything. Never follow symlinks.
    conflicts = []
    for dest in files:
        reject_symlinks(dest)
        if dest.exists():
            if not dest.is_file():
                raise ValueError(f"destination is not a regular file: {dest}")
            conflicts.append(dest)
    if conflicts and not args.backup_existing:
        raise ValueError("existing destinations (unchanged; use --apply --backup-existing to replace): " + ", ".join(map(str, conflicts)))
    if not args.apply:
        for dest in files:
            print(f"DRY RUN: would create {dest}")
        return
    for dest, text in files.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            # Exclusive creation avoids silently replacing an earlier backup.
            backup = dest.with_name(dest.name + ".backup")
            index = 1
            while backup.exists():
                backup = dest.with_name(dest.name + f".backup.{index}")
                index += 1
            fd_backup = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd_backup, "wb") as out, dest.open("rb") as source:
                shutil.copyfileobj(source, out)
            print(f"BACKUP: {backup}")
        fd, temp = tempfile.mkstemp(prefix=".hermes-starter-", dir=dest.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                out.write(text)
            os.chmod(temp, 0o600)
            os.replace(temp, dest)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        print(f"WROTE: {dest}")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        render(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
