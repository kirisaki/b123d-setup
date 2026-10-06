# b123d-setup

A small CLI for creating build123d CAD projects managed by uv.
The generator has no runtime dependencies. CAD dependencies are installed in
each generated project's own environment.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uvx --from git+https://github.com/kirisaki/b123-setup.git b123d-setup my-part --with-vscode
cd my-part
uv run -m scripts.export_all
```

To use a local checkout, run this from the repository directory instead:

```sh
uvx --from . b123d-setup my-part --with-vscode
```

The generator only creates files. The first `uv run` or `uv sync` in the generated
project installs its dependencies and creates `.venv` and `uv.lock`. Generated
projects use Python 3.11; uv downloads it if needed. Commit `uv.lock` to preserve
the resolved dependency versions.

## Preview in VS Code

Open the generated project in VS Code and install the recommended Python and
OCP CAD Viewer extensions. Start OCP CAD Viewer, then run:

```sh
uv run main.py
```

Edit `parts/base_plate.py` and run the command again to preview your changes.
For F5 debugging, run `uv sync` first and select the project's `.venv` interpreter.

## CLI

```text
b123d-setup DIRECTORY [--with-vscode]
b123d-setup --name DIRECTORY [--with-vscode]
b123d-setup --help
b123d-setup --version
```

- Create a project in a new directory or an existing empty directory.
- Nonempty directories are rejected; existing files are never overwritten.
- `--with-vscode` adds settings, launch configurations, and extension recommendations.

## Generated project

```text
my-part/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
├── main.py
├── parts/
│   ├── __init__.py
│   └── base_plate.py
├── assembly/
├── scripts/
│   ├── __init__.py
│   └── export_all.py
├── exports/
└── .vscode/              # With --with-vscode
```

The sample is a 60 × 40 × 3 mm plate with six 3 mm diameter through holes.
Run `uv run -m scripts.export_all` from the project directory to export STEP
and STL files into `exports/`. Exporting does not require a viewer.

Jupyter is optional. Start it in the generated project with:

```sh
uv run --extra notebook jupyter lab
```

## Development and building

```sh
uv run python -m unittest discover -s tests -v
uv build
uvx --from ./dist/b123d_setup-0.1.0-py3-none-any.whl b123d-setup --help
```

Building creates a wheel and source distribution in `dist/`.
After the first PyPI release, install and run it with:

```sh
uvx b123d-setup my-part --with-vscode
```

## Publishing

The `publish.yml` workflow tests and builds the package on pushes to `main`
and pull requests. Only a manual run from `main` publishes to PyPI, using
Trusted Publishing with the GitHub environment `pypi`. No API token is needed.

For the first release, register a pending publisher at
[PyPI Publishing](https://pypi.org/manage/account/publishing/) with:

| Field | Value |
| --- | --- |
| PyPI project name | `b123d-setup` |
| GitHub owner | `kirisaki` |
| Repository | `b123-setup` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

Then open **Actions → Build and publish to PyPI → Run workflow** and select
`main`. Each subsequent release needs a new version in `pyproject.toml` and
an updated `uv.lock` before running the workflow again.
