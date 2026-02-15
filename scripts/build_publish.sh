#!/usr/bin/env bash
# Build and/or publish FORMAL to PyPI.
#
# Usage:
#   ./scripts/build_publish.sh build       # build only
#   ./scripts/build_publish.sh publish     # publish only (assumes dist/ exists)
#   ./scripts/build_publish.sh all         # build + publish
#   ./scripts/build_publish.sh testpublish # publish to TestPyPI
#
# Requirements:
#   pipx install build   (or: pip install build)
#   pipx install twine   (or: pip install twine)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

red()   { printf '\033[1;31m%s\033[0m\n' "$*"; }
green() { printf '\033[1;32m%s\033[0m\n' "$*"; }
bold()  { printf '\033[1m%s\033[0m\n' "$*"; }

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
    grep '^version' "$ROOT/pyproject.toml" | head -1 | sed 's/.*"\(.*\)".*/\1/'
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
    *)
        echo "Usage: $0 {build|publish|testpublish|all}"
        echo
        echo "Commands:"
        echo "  build        Clean and build sdist + wheel"
        echo "  publish      Upload dist/ to PyPI"
        echo "  testpublish  Upload dist/ to TestPyPI"
        echo "  all          Build then publish to PyPI"
        exit 1
        ;;
esac
