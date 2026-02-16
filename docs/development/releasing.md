---
title: Releasing
---

# Releasing a New Version

A release script at `scripts/build_publish.sh` automates the full release pipeline.

## One-Command Release

```bash
./scripts/build_publish.sh release 1.0.0
```

This runs through every step with a confirmation prompt upfront:

| Step | Action | Aborts if... |
|------|--------|-------------|
| Pre-flight | Checks clean working tree, tag doesn't exist | Uncommitted changes or tag collision |
| 1. Bump | Updates version in `pyproject.toml` and `src/formal/__init__.py` | Invalid format or already at that version |
| 2. Commit | `git commit -m "release: v1.0.0"` | |
| 3. Build | Clean build of sdist + wheel, validates with twine | Build or validation failure |
| 4. Test | Installs wheel via pipx, checks `--version` and `--help` | Version mismatch or broken CLI |
| 5. Tag | `git tag -a v1.0.0 -m "Release v1.0.0"` | |
| 6. Publish | `twine upload dist/*` to PyPI | Upload failure |
| 7. Push | Pushes commit and tag to origin | |

## Individual Steps

Each step is also available standalone for more control:

```bash
# Bump version without committing (useful for pre-release tweaks)
./scripts/build_publish.sh bump 0.2.0

# Build and validate only
./scripts/build_publish.sh build

# Smoke-test the built wheel
./scripts/build_publish.sh test

# Publish to TestPyPI first (dry run)
./scripts/build_publish.sh testpublish

# Publish to PyPI (assumes dist/ already built)
./scripts/build_publish.sh publish

# Build + publish in one go (no version bump)
./scripts/build_publish.sh all
```

## Where the Version Lives

The version is stored in two files that the `bump` / `release` commands update together:

| File | Line | Used by |
|------|------|---------|
| `pyproject.toml` | `version = "X.Y.Z"` | PyPI, build tools |
| `src/formal/__init__.py` | `__version__ = "X.Y.Z"` | `formal --version`, runtime |

## Requirements for Publishing

- A [PyPI account](https://pypi.org/account/register/) with an [API token](https://pypi.org/manage/account/token/)
- `build` and `twine` available via pip or pipx (the script auto-detects both)
