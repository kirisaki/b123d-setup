"""Command-line entry point; CAD dependencies belong to generated projects."""

import argparse
from importlib.metadata import version
import os
from pathlib import Path
import re
import shlex
import sys

from .templates import project_files


def project_name(directory: Path) -> str:
    """Turn a directory basename into a valid Python distribution name."""
    return re.sub(r"[^a-z0-9]+", "-", directory.name.lower()).strip("-") or "cad-project"


def create_project(root: Path, with_vscode: bool = False) -> None:
    if root.exists():
        if not root.is_dir():
            raise ValueError(f"'{root}' is not a directory.")
        if any(root.iterdir()):
            raise ValueError(f"'{root}' already exists and is not empty.")

    files = project_files(project_name(root), with_vscode=with_vscode)
    root.mkdir(parents=True, exist_ok=True)
    for name in ("parts", "assembly", "exports", "scripts"):
        (root / name).mkdir(exist_ok=True)
    for relative, content in files.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a uv-managed build123d project (no dependencies installed)."
    )
    parser.add_argument("directory", nargs="?", help="Project directory to create.")
    parser.add_argument("--name", help="Legacy alias for the project directory.")
    parser.add_argument(
        "--with-vscode", action="store_true",
        help="Generate VS Code settings, launch configurations and extension recommendations.",
    )
    parser.add_argument("--version", action="version", version=version("b123d-setup"))
    args = parser.parse_args(argv)
    if args.directory is not None and args.name is not None:
        parser.error("use either DIRECTORY or --name, not both")
    directory = args.directory if args.directory is not None else args.name
    if not directory or not directory.strip():
        parser.error("a project directory is required")

    try:
        root = Path(directory).expanduser().resolve()
        create_project(root, with_vscode=args.with_vscode)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    # Quote for POSIX shells or PowerShell, including paths containing spaces.
    if os.name == "nt":
        quoted_root = "'" + str(root).replace("'", "''") + "'"
    else:
        quoted_root = shlex.quote(str(root))
    print(f"Initialized build123d project at: {root}")
    print(f"\nNext steps:\n  cd {quoted_root}\n  uv run -m scripts.export_all")
    print("\nPreview with OCP CAD Viewer running:\n  uv run main.py")
    return 0
