"""Small, self-contained templates shipped inside the wheel."""

import json


PYPROJECT = '''\
[project]
name = "{name}"
version = "0.1.0"
description = "A build123d CAD project"
requires-python = ">=3.11,<3.15"
dependencies = [
    "build123d>=0.13,<0.14",
    "ocp-vscode>=4.1,<5",
]

[project.optional-dependencies]
notebook = ["jupyter"]

[tool.uv]
package = false
'''

README = '''\
# {name}

A parametric CAD project using build123d. All sample dimensions are in millimetres.
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first.
Run the following commands from this project directory.

## Export STEP and STL

```sh
uv run -m scripts.export_all
```

The first run installs Python 3.11 if necessary, creates `.venv`, resolves
dependencies and writes `uv.lock`. Commit `uv.lock` to preserve those versions.
The generated files are `exports/base_plate.step` and `exports/base_plate.stl`.
Exporting does not require a viewer. The output path is relative to this project,
not the current working directory.

## Preview

Install the VS Code Python and OCP CAD Viewer extensions, open this directory
in VS Code, and start OCP CAD Viewer before running:

```sh
uv run main.py
```

For F5 debugging, run `uv sync` first and select this project's `.venv` interpreter
in VS Code. If generated with `--with-vscode`, launch configurations are included.

## Model structure

- `parts/`: functions that construct parts; start with `base_plate.py`.
- `assembly/`: space for assemblies as the project grows.
- `main.py`: preview the model.
- `scripts/export_all.py`: explicitly list and export the project's models.
- `exports/`: generated output, ignored by Git.

Keep modelling independent of preview and export, so the same part can be used
in both. Add new parts to the preview and export scripts as needed.

## Optional notebooks

```sh
uv run --extra notebook jupyter lab
```
'''

GITIGNORE = '''\
.venv/
__pycache__/
.ipynb_checkpoints/
exports/
.DS_Store
'''

MAIN = '''\
from ocp_vscode import show

from parts.base_plate import base_plate


if __name__ == "__main__":
    show(base_plate())
'''

BASE_PLATE = '''\
from build123d import Box, BuildPart, GridLocations, Hole, Part


def base_plate(length=60, width=40, thickness=3, hole_d=3) -> Part:
    """A plate with six through holes; dimensions and hole diameter are in mm."""
    with BuildPart() as plate:
        Box(length, width, thickness)
        with GridLocations(15, 15, 3, 2):
            Hole(radius=hole_d / 2)
    return plate.part
'''

EXPORT_ALL = '''\
from pathlib import Path

from build123d import export_step, export_stl

from parts.base_plate import base_plate


def main():
    exports = Path(__file__).resolve().parents[1] / "exports"
    exports.mkdir(exist_ok=True)
    part = base_plate()
    for exporter, extension in ((export_step, "step"), (export_stl, "stl")):
        destination = exports / f"base_plate.{extension}"
        if not exporter(part, destination):
            raise RuntimeError(f"Export failed: {destination}")
        print(f"Exported: {destination}")


if __name__ == "__main__":
    main()
'''


def project_files(name: str, *, with_vscode: bool) -> dict[str, str]:
    files = {
        "pyproject.toml": PYPROJECT.format(name=name),
        ".python-version": "3.11\n",
        ".gitignore": GITIGNORE,
        "README.md": README.format(name=name),
        "main.py": MAIN,
        "parts/__init__.py": "",
        "parts/base_plate.py": BASE_PLATE,
        "scripts/__init__.py": "",
        "scripts/export_all.py": EXPORT_ALL,
    }
    if with_vscode:
        configurations = {
            "settings": {"python.defaultInterpreterPath": "${workspaceFolder}/.venv"},
            "extensions": {"recommendations": [
                "ms-python.python", "ms-python.debugpy", "bernhard-42.ocp-cad-viewer",
            ]},
            "launch": {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Preview main.py", "type": "debugpy", "request": "launch",
                        "program": "${workspaceFolder}/main.py",
                        "cwd": "${workspaceFolder}", "console": "integratedTerminal",
                    },
                    {
                        "name": "Export all", "type": "debugpy", "request": "launch",
                        "module": "scripts.export_all",
                        "cwd": "${workspaceFolder}", "console": "integratedTerminal",
                    },
                ],
            },
        }
        for filename, contents in configurations.items():
            files[f".vscode/{filename}.json"] = json.dumps(contents, indent=2) + "\n"
    return files
