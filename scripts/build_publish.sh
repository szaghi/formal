#!/usr/bin/env bash
# Build, publish, and release FORMAL to PyPI.
#
# Usage:
#   ./scripts/build_publish.sh build                # build only
#   ./scripts/build_publish.sh publish              # publish only (assumes dist/ exists)
#   ./scripts/build_publish.sh testpublish          # publish to TestPyPI
#   ./scripts/build_publish.sh all                  # build + publish
#   ./scripts/build_publish.sh release <version>    # full release: bump, build, publish, tag, push
#   ./scripts/build_publish.sh release 1.0.0        # example: release v1.0.0
#
# Requirements:
#   pipx install build   (or: pip install build)
#   pipx install twine   (or: pip install twine)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
PYPROJECT="$ROOT/pyproject.toml"
INIT_PY="$ROOT/src/formal/__init__.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

red()   { printf '\033[1;31m%s\033[0m\n' "$*"; }
green() { printf '\033[1;32m%s\033[0m\n' "$*"; }
bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
dim()   { printf '\033[2m%s\033[0m\n' "$*"; }

die() { red "Error: $*" >&2; exit 1; }

check_tool() {
    command -v "$1" >/dev/null 2>&1 || die "'$1' not found. Install with: pipx install $1"
}

# Run a Python tool: tries 'python3 -m <tool>' first, falls back to 'pipx run <tool>'
run_tool() {
    local tool="$1"; shift
    if python3 -m "$tool" --help >/dev/null 2>&1; then
        python3 -m "$tool" "$@"
    elif command -v pipx >/dev/null 2>&1; then
        pipx run "$tool" "$@"
    else
        die "'$tool' not available via python3 -m or pipx. Install with: pipx install $tool"
    fi
}

# Extract version from pyproject.toml
get_version() {
    grep '^version' "$PYPROJECT" | head -1 | sed 's/.*"\(.*\)".*/\1/'
}

# Validate semver format (loose: X.Y.Z with optional pre-release)
validate_version() {
    local v="$1"
    if ! echo "$v" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+([a-zA-Z0-9._-]*)?$'; then
        die "Invalid version '$v'. Expected format: X.Y.Z (e.g. 1.0.0, 0.2.0rc1)"
    fi
}

# ---------------------------------------------------------------------------
# Version bump
# ---------------------------------------------------------------------------

do_bump() {
    local new_version="$1"
    local old_version
    old_version="$(get_version)"

    validate_version "$new_version"

    if [ "$old_version" = "$new_version" ]; then
        die "Version is already $new_version"
    fi

    bold "Bumping version: $old_version -> $new_version"

    # Update pyproject.toml
    sed -i "s/^version = \".*\"/version = \"$new_version\"/" "$PYPROJECT"
    green "  Updated pyproject.toml"

    # Update __init__.py
    sed -i "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" "$INIT_PY"
    green "  Updated src/formal/__init__.py"

    # Verify both files agree
    local v1 v2
    v1="$(get_version)"
    v2="$(grep '^__version__' "$INIT_PY" | sed 's/.*"\(.*\)".*/\1/')"
    if [ "$v1" != "$new_version" ] || [ "$v2" != "$new_version" ]; then
        die "Version mismatch after bump: pyproject.toml=$v1, __init__.py=$v2"
    fi
    green "  Verified: both files set to $new_version"
}

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

do_build() {
    check_tool python3

    local version
    version="$(get_version)"
    bold "Building formal-ford2vitepress v${version}..."

    # Clean previous build
    rm -rf "$DIST" "$ROOT/build" "$ROOT"/src/*.egg-info
    green "  Cleaned previous artifacts"

    # Build sdist + wheel
    run_tool build "$ROOT"
    green "  Built sdist + wheel"

    # Validate
    run_tool twine check "$DIST"/*
    green "  Validation passed"

    echo
    bold "Artifacts:"
    ls -lh "$DIST"/
}

# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

do_test() {
    local version
    version="$(get_version)"

    bold "Smoke-testing v${version}..."

    local whl
    whl="$(ls "$DIST"/*.whl 2>/dev/null | head -1)"
    [ -n "$whl" ] || die "No wheel found. Run '$0 build' first."

    # Install into pipx and verify
    pipx install --force "$whl" >/dev/null 2>&1
    local installed_version
    installed_version="$(formal --version 2>&1 | awk '{print $NF}')"
    if [ "$installed_version" != "$version" ]; then
        die "Version mismatch: expected $version, got $installed_version"
    fi
    green "  formal --version reports $installed_version"

    # Verify help works
    formal --help >/dev/null 2>&1
    green "  formal --help OK"

    formal init --help >/dev/null 2>&1
    green "  formal init --help OK"

    formal generate --help >/dev/null 2>&1
    green "  formal generate --help OK"

    green "  Smoke tests passed"
}

# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------

do_publish() {
    local repo="${1:-pypi}"

    check_tool python3

    [ -d "$DIST" ] || die "No dist/ directory found. Run '$0 build' first."
    [ -n "$(ls "$DIST"/*.whl 2>/dev/null)" ] || die "No wheel found in dist/. Run '$0 build' first."

    local version
    version="$(get_version)"

    # Check git status
    if command -v git >/dev/null 2>&1 && [ -d "$ROOT/.git" ]; then
        if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
            red "Warning: uncommitted changes in working tree."
            read -rp "Continue anyway? [y/N] " answer
            [ "$answer" = "y" ] || [ "$answer" = "Y" ] || exit 1
        fi

        # Check if version tag exists
        if ! git -C "$ROOT" tag -l "v${version}" | grep -q .; then
            read -rp "Tag v${version} does not exist. Create it? [Y/n] " answer
            if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
                git -C "$ROOT" tag -a "v${version}" -m "Release v${version}"
                green "  Created tag v${version}"
            fi
        fi
    fi

    if [ "$repo" = "testpypi" ]; then
        bold "Publishing v${version} to TestPyPI..."
        run_tool twine upload --repository testpypi "$DIST"/*
        echo
        green "Done! Test install with:"
        echo "  pipx install --index-url https://test.pypi.org/simple/ --pip-args='--extra-index-url https://pypi.org/simple/' formal-ford2vitepress"
    else
        bold "Publishing v${version} to PyPI..."
        run_tool twine upload "$DIST"/*
        echo
        green "Done! Install with:"
        echo "  pipx install formal-ford2vitepress"
    fi
}

# ---------------------------------------------------------------------------
# Full release
# ---------------------------------------------------------------------------

do_release() {
    local new_version="$1"

    validate_version "$new_version"
    check_tool git
    check_tool python3

    local old_version
    old_version="$(get_version)"

    echo
    bold "=== FORMAL Release: v${old_version} -> v${new_version} ==="
    echo
    dim "  This will:"
    dim "    1. Bump version in pyproject.toml and __init__.py"
    dim "    2. Commit the version bump"
    dim "    3. Build sdist + wheel and validate"
    dim "    4. Run smoke tests"
    dim "    5. Create git tag v${new_version}"
    dim "    6. Publish to PyPI"
    dim "    7. Push commit and tag to origin"
    echo
    read -rp "Proceed? [y/N] " answer
    [ "$answer" = "y" ] || [ "$answer" = "Y" ] || { echo "Aborted."; exit 0; }

    # Pre-flight checks
    if [ -n "$(git -C "$ROOT" status --porcelain)" ]; then
        die "Working tree has uncommitted changes. Commit or stash them first."
    fi

    if git -C "$ROOT" tag -l "v${new_version}" | grep -q .; then
        die "Tag v${new_version} already exists."
    fi

    echo

    # Step 1: Bump version
    do_bump "$new_version"
    echo

    # Step 2: Commit
    bold "Committing version bump..."
    git -C "$ROOT" add "$PYPROJECT" "$INIT_PY"
    git -C "$ROOT" commit -m "release: v${new_version}"
    green "  Committed"
    echo

    # Step 3: Build
    do_build
    echo

    # Step 4: Smoke test
    do_test
    echo

    # Step 5: Tag
    bold "Creating tag v${new_version}..."
    git -C "$ROOT" tag -a "v${new_version}" -m "Release v${new_version}"
    green "  Tagged v${new_version}"
    echo

    # Step 6: Publish
    bold "Publishing to PyPI..."
    run_tool twine upload "$DIST"/*
    green "  Published to PyPI"
    echo

    # Step 7: Push
    bold "Pushing to origin..."
    local branch
    branch="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)"
    git -C "$ROOT" push origin "$branch"
    git -C "$ROOT" push origin "v${new_version}"
    green "  Pushed $branch + tag v${new_version}"

    echo
    bold "=== Release v${new_version} complete! ==="
    echo
    echo "  PyPI:   https://pypi.org/project/formal-ford2vitepress/${new_version}/"
    echo "  GitHub: https://github.com/szaghi/formal/releases/tag/v${new_version}"
    echo
    echo "  Install: pipx install formal-ford2vitepress==${new_version}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "${1:-}" in
    build)
        do_build
        ;;
    publish)
        do_publish pypi
        ;;
    testpublish)
        do_publish testpypi
        ;;
    all)
        do_build
        echo
        do_publish pypi
        ;;
    release)
        [ -n "${2:-}" ] || die "Usage: $0 release <version>  (e.g. $0 release 1.0.0)"
        do_release "$2"
        ;;
    bump)
        [ -n "${2:-}" ] || die "Usage: $0 bump <version>  (e.g. $0 bump 1.0.0)"
        do_bump "$2"
        ;;
    test)
        do_test
        ;;
    *)
        echo "Usage: $0 <command> [args]"
        echo
        echo "Commands:"
        echo "  build              Clean and build sdist + wheel"
        echo "  test               Smoke-test the built wheel via pipx"
        echo "  publish            Upload dist/ to PyPI"
        echo "  testpublish        Upload dist/ to TestPyPI"
        echo "  all                Build then publish to PyPI"
        echo "  bump <version>     Bump version in pyproject.toml + __init__.py"
        echo "  release <version>  Full release: bump, commit, build, test, tag, publish, push"
        echo
        echo "Examples:"
        echo "  $0 release 1.0.0   # major release"
        echo "  $0 release 0.2.0   # minor release"
        echo "  $0 release 0.1.1   # patch release"
        echo "  $0 build           # build only, no publish"
        exit 1
        ;;
esac
