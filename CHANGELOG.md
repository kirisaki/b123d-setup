# Changelog

## Unreleased

### Fixed

- Generate projects with `ocp-vscode>=4.1,<5` so the viewer works with
  build123d 0.13 and its OCP 8 dependency. The previous 3.x constraint caused
  an import error for `TopTools_IndexedDataMapOfShapeListOfShape`.

### Added

- Check generated projects in CI by importing the viewer, constructing a valid
  sample part, and exporting STEP and STL files before publishing.

## 0.1.0 - 2026-10-06

### Added

- Publish the `b123d-setup` CLI for use through `uvx`.
- Generate uv-managed CAD projects with a parametric sample plate, preview
  script, and STEP/STL export script.
- Provide optional VS Code configuration and Jupyter dependencies.
- Reject nonempty destination directories to preserve existing files.
- Build, validate, and publish packages through GitHub Actions using PyPI
  Trusted Publishing.
