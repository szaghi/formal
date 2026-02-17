"""Command-line interface for FORMAL.

Provides two main commands:
  - init:     Scaffold a VitePress docs site with FORD project file
  - generate: Generate API Markdown from Fortran sources
"""

import argparse
import sys
from pathlib import Path

from formal import __version__


def main(argv=None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="formal",
        description="FORMAL: generate VitePress API docs from FORD-parsed Fortran sources.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- init command ---
    init_parser = subparsers.add_parser(
        "init",
        help="Scaffold a VitePress docs site with FORD project file",
        description="Create the minimal files needed: FORD project file, VitePress config, "
        "package.json, and landing page. Existing files are never overwritten.",
    )
    init_parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Root directory of the Fortran project (default: current directory)",
    )
    init_parser.add_argument(
        "--name",
        default=None,
        help="Project name (default: directory name)",
    )
    init_parser.add_argument(
        "--src-dir",
        nargs="+",
        default=None,
        help="Source directories relative to project root (default: auto-detect src/)",
    )
    init_parser.add_argument(
        "--exclude-dir",
        nargs="*",
        default=None,
        help="Directories to exclude from FORD parsing",
    )
    init_parser.add_argument(
        "--docs-dir",
        default="docs",
        help="Documentation directory relative to project root (default: docs)",
    )
    init_parser.add_argument(
        "--ford-file",
        default=None,
        help="Path for FORD project file (default: docs/formal.md)",
    )
    init_parser.add_argument(
        "--docmark",
        default="<",
        help="FORD doc comment marker (default: '<' for '!<' comments)",
    )
    init_parser.add_argument(
        "--author",
        default="",
        help="Author name",
    )
    init_parser.add_argument(
        "--no-math",
        action="store_true",
        help="Disable LaTeX math support",
    )
    init_parser.add_argument(
        "--no-fortran-highlight",
        action="store_true",
        help="Disable Fortran syntax highlighting aliases",
    )
    init_parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Add vitepress-plugin-mermaid to package.json and wrap config with withMermaid",
    )

    # --- generate command ---
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate API documentation from Fortran sources",
        description="Parse Fortran sources using FORD and generate VitePress-compatible "
        "Markdown files with sidebar JSON.",
    )
    gen_parser.add_argument(
        "--project",
        default=None,
        help="FORD project file (default: auto-detect)",
    )
    gen_parser.add_argument(
        "--output",
        default=None,
        help="Output directory for Markdown files (default: docs/api)",
    )
    gen_parser.add_argument(
        "--src-root",
        default=None,
        help="Root path to strip from source file paths in output",
    )
    gen_parser.add_argument(
        "--mirror-sources",
        action="store_true",
        help="Mirror source directory structure in output (e.g. api/src/lib/module.md)",
    )
    gen_parser.add_argument(
        "--diagrams",
        action="store_true",
        help="Embed Mermaid dependency, inheritance, and call-graph diagrams in each page",
    )
    gen_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        return cmd_init(args)
    elif args.command == "generate":
        return cmd_generate(args)


def cmd_init(args) -> int:
    """Handle the 'init' command."""
    from formal.scaffold import create_ford_project_file, init_vitepress_site

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(f"Error: {project_root} is not a directory", file=sys.stderr)
        return 1

    project_name = args.name or project_root.name.upper()
    docs_dir = project_root / args.docs_dir

    # Auto-detect source directories
    src_dirs = args.src_dir
    if src_dirs is None:
        src_dir = project_root / "src"
        if src_dir.is_dir():
            # Check for common sub-structures
            candidates = []
            for sub in ["lib", "app", "mod", "modules", "src"]:
                if (src_dir / sub).is_dir():
                    candidates.append(f"../src/{sub}")
            if not candidates:
                candidates = ["../src"]
            src_dirs = candidates
        else:
            # No src/ directory, use project root
            src_dirs = [".."]
        print(f"  Auto-detected source dirs: {src_dirs}")

    # Auto-detect exclude dirs
    exclude_dirs = args.exclude_dir
    if exclude_dirs is None:
        exclude_dirs = []
        for pattern in ["third_party", "third_party_manual", "external", "vendor"]:
            for candidate in project_root.rglob(pattern):
                if candidate.is_dir():
                    rel = f"../{candidate.relative_to(project_root)}"
                    exclude_dirs.append(rel + "/")
        if exclude_dirs:
            print(f"  Auto-detected exclude dirs: {exclude_dirs}")

    # Create FORD project file
    ford_file = Path(args.ford_file) if args.ford_file else project_root / "doc" / "formal.md"
    print(f"\nCreating FORD project file: {ford_file}")
    create_ford_project_file(
        output_path=ford_file,
        project_name=project_name,
        src_dirs=src_dirs,
        exclude_dirs=exclude_dirs,
        docmark=args.docmark,
        author=args.author,
    )
    print(f"  Created {ford_file}")

    # Scaffold VitePress site
    print(f"\nScaffolding VitePress site in: {docs_dir}")
    init_vitepress_site(
        docs_dir=docs_dir,
        project_name=project_name,
        enable_math=not args.no_math,
        enable_fortran=not args.no_fortran_highlight,
        enable_mermaid=args.mermaid,
    )

    print(f"\nDone! Next steps:")
    print(f"  1. cd {docs_dir} && npm install")
    print(f"  2. formal generate --project {ford_file.relative_to(project_root)}")
    print(f"  3. cd {docs_dir} && npm run docs:dev")
    return 0


def cmd_generate(args) -> int:
    """Handle the 'generate' command."""
    from formal.generator import generate

    # Find project file
    project_file = None
    if args.project:
        project_file = Path(args.project).resolve()
    else:
        # Auto-detect
        for candidate in ["doc/ford.md", "doc/main_page.md", "doc/formal.md", "doc/vitepress.md",
                          "docs/ford.md", "docs/main_page.md", "docs/formal.md", "docs/vitepress.md"]:
            p = Path(candidate)
            if p.exists():
                project_file = p.resolve()
                break

    if project_file is None or not project_file.exists():
        print("Error: no FORD project file found.", file=sys.stderr)
        print("  Provide --project or run 'formal init' first.", file=sys.stderr)
        return 1

    # Find output directory
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        # Default: docs/api relative to project file's parent's parent
        # (project file is typically in doc/, docs is sibling)
        project_root = project_file.parent.parent
        output_dir = project_root / "docs" / "api"

    result = generate(
        project_file=project_file,
        output_dir=output_dir,
        src_root=args.src_root,
        mirror_sources=args.mirror_sources,
        diagrams=args.diagrams,
        verbose=not args.quiet,
    )

    return 0 if result["modules"] > 0 else 1
