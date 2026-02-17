"""Core API documentation generator.

Parses Fortran sources via FORD and generates VitePress-compatible Markdown files.
"""

import json
import re
from pathlib import Path
from typing import Any, Optional


def load_project(project_file: Path):
    """Parse Fortran sources using FORD's project file and return a correlated Project.

    Args:
        project_file: Path to a FORD project file (.md format with metadata header).

    Returns:
        A FORD Project object with all modules parsed and cross-referenced.
    """
    from ford.settings import load_markdown_settings
    import ford.fortran_project

    project_text = project_file.read_text(encoding="utf-8")
    directory = str(project_file.parent)

    settings, _ = load_markdown_settings(directory, project_text, str(project_file))
    settings.normalise_paths(directory)

    project = ford.fortran_project.Project(settings)
    project.correlate()
    return project


# ---------------------------------------------------------------------------
# Text formatting helpers
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(
    r"\[\[(\w+(?:\.\w+)?)(?:\((\w+)\))?(?::(\w+)(?:\((\w+)\))?)?\]\]"
)
_TYPE_PAREN_RE = re.compile(r"\b(type|class)\((\w+)\)", re.IGNORECASE)
_KIND_EQ_RE = re.compile(r"\bkind=(\w+)", re.IGNORECASE)


def slugify(name: str) -> str:
    """Convert an entity name to a VitePress-compatible anchor slug.

    VitePress (via @mdit-vue/shared) lowercases heading text and replaces
    runs of whitespace, underscores, and hyphens with a single hyphen, so
    ``strf_r8p`` becomes ``strf-r8p`` in the rendered HTML anchor.
    """
    return re.sub(r"[\s_-]+", "-", name.lower()).strip("-")


def build_entity_index(project, api_prefix: str = "/api/") -> dict[str, str]:
    """Build a lowercase name→URL mapping from the FORD project's entity graph.

    Supports bare name lookup (``foo``) and compound ``parent:child`` lookup.
    Variables are not indexed (they have no heading anchors).

    Args:
        project: A correlated FORD Project object.
        api_prefix: URL prefix for API pages (default: '/api/').

    Returns:
        A dict mapping lowercased entity names to their VitePress URL strings.
    """
    prefix = api_prefix.rstrip("/")
    index: dict[str, str] = {}

    for module in project.modules:
        mod_key = module.name.lower()
        index[mod_key] = f"{prefix}/{module.name}"

        for dtype in module.types:
            url = f"{prefix}/{module.name}#{slugify(dtype.name)}"
            index[dtype.name.lower()] = url
            index[f"{mod_key}:{dtype.name.lower()}"] = url

        for proc in list(module.subroutines) + list(module.functions):
            url = f"{prefix}/{module.name}#{slugify(proc.name)}"
            index[proc.name.lower()] = url
            index[f"{mod_key}:{proc.name.lower()}"] = url

        for iface in module.interfaces:
            url = f"{prefix}/{module.name}#{slugify(iface.name)}"
            index[iface.name.lower()] = url
            index[f"{mod_key}:{iface.name.lower()}"] = url

        for var in module.variables:
            index[var.name.lower()] = f"{prefix}/{module.name}"

    return index


def resolve_links(text: str, index: dict[str, str]) -> str:
    """Replace FORD ``[[name]]`` cross-references with VitePress Markdown links.

    If the referenced entity is found in *index* the marker becomes
    ``[display](url)``; otherwise just the display name is used (no broken link).

    Args:
        text: Raw documentation text that may contain ``[[...]]`` markers.
        index: Name→URL mapping built by :func:`build_entity_index`.

    Returns:
        Text with all ``[[...]]`` markers resolved.
    """
    def _replace(m: re.Match) -> str:
        parent = m.group(1)
        child = m.group(3)

        if child:
            display = child
            key = f"{parent.lower()}:{child.lower()}"
            fallback_key = child.lower()
        else:
            display = parent
            key = parent.lower()
            fallback_key = None

        url = index.get(key)
        if url is None and fallback_key is not None:
            url = index.get(fallback_key)

        if url:
            return f"[{display}]({url})"
        return display

    return _LINK_RE.sub(_replace, text)


def linkify_type_str(text: str, index: dict[str, str]) -> str:
    """Insert Markdown links into a plain Fortran type string.

    Recognises ``type(name)`` / ``class(name)`` and ``kind=name`` patterns.
    If the name is present in *index* the name is replaced with a Markdown
    link; otherwise the text is left unchanged.

    Args:
        text: A plain (HTML-stripped) Fortran type string.
        index: Name→URL mapping built by :func:`build_entity_index`.

    Returns:
        The type string with known names turned into Markdown links.
    """
    def _replace_type(m: re.Match) -> str:
        keyword = m.group(1)
        name = m.group(2)
        url = index.get(name.lower())
        if url:
            return f"{keyword}([{name}]({url}))"
        return m.group(0)

    def _replace_kind(m: re.Match) -> str:
        name = m.group(1)
        url = index.get(name.lower())
        if url:
            return f"kind=[{name}]({url})"
        return m.group(0)

    text = _TYPE_PAREN_RE.sub(_replace_type, text)
    text = _KIND_EQ_RE.sub(_replace_kind, text)
    return text


def strip_html(text: str) -> str:
    """Strip HTML tags from text (FORD adds <a href=...> links after correlate)."""
    return re.sub(r"<[^>]+>", "", text)


def escape_pipe(text: str) -> str:
    """Escape pipe characters for Markdown tables."""
    return text.replace("|", "\\|")


def format_doc(doc_list: list, link_index: Optional[dict] = None) -> str:
    """Join raw doc_list lines into a Markdown string."""
    if not doc_list:
        return ""
    text = "\n".join(doc_list).strip()
    if link_index is not None and text:
        text = resolve_links(text, link_index)
    return text


def inline_doc(doc_list: list, link_index: Optional[dict] = None) -> str:
    """Format doc_list as a single-line table cell (first line only for brevity)."""
    if not doc_list:
        return ""
    for line in doc_list:
        stripped = line.strip()
        if stripped:
            if link_index is not None:
                stripped = resolve_links(stripped, link_index)
            return escape_pipe(strip_html(stripped))
    return ""


def format_type_str(var, link_index: Optional[dict] = None) -> str:
    """Get a display string for a variable's Fortran type."""
    try:
        ft = var.full_type
        if ft:
            s = strip_html(str(ft))
            if link_index:
                s = linkify_type_str(s, link_index)
            return escape_pipe(s)
    except Exception:
        pass
    s = str(var.vartype) if var.vartype else ""
    if hasattr(var, "kind") and var.kind:
        s += f"({var.kind})"
    s = strip_html(s)
    if link_index:
        s = linkify_type_str(s, link_index)
    return escape_pipe(s)


def format_attribs(var) -> str:
    """Format variable attributes as a comma-separated string."""
    parts = []
    if hasattr(var, "attribs") and var.attribs:
        parts.extend(str(a) for a in var.attribs)
    if hasattr(var, "optional") and var.optional:
        parts.append("optional")
    if hasattr(var, "parameter") and var.parameter:
        parts.append("parameter")
    return escape_pipe(", ".join(parts))


# ---------------------------------------------------------------------------
# Source path extraction
# ---------------------------------------------------------------------------

def get_source_path(module, src_root: Optional[str] = None) -> str:
    """Get the relative source file path for a module.

    Args:
        module: A FORD FortranModule object.
        src_root: Optional prefix to strip (e.g. '/home/user/myproject/').
                  If None, tries to find 'src/' in the path.

    Returns:
        A relative path string like 'src/lib/common/foo.F90'.
    """
    if hasattr(module, "parent") and hasattr(module.parent, "path"):
        full = str(module.parent.path)
        if src_root:
            src_root_str = str(src_root).rstrip("/")
            if full.startswith(src_root_str):
                return full[len(src_root_str):].lstrip("/")
        # Fallback: find 'src/' in path
        idx = full.find("/src/")
        if idx >= 0:
            return full[idx + 1:]
        return full
    return getattr(module, "filename", "")


# ---------------------------------------------------------------------------
# Entity formatters
# ---------------------------------------------------------------------------

def format_variable_table(
    variables: list,
    show_intent: bool = False,
    link_index: Optional[dict] = None,
) -> str:
    """Generate a Markdown table for a list of variables."""
    if not variables:
        return ""

    if show_intent:
        lines = [
            "| Name | Type | Intent | Attributes | Description |",
            "|------|------|--------|------------|-------------|",
        ]
    else:
        lines = [
            "| Name | Type | Attributes | Description |",
            "|------|------|------------|-------------|",
        ]

    for var in variables:
        name = f"`{var.name}`" if hasattr(var, "name") else str(var)
        vtype = format_type_str(var, link_index)
        attribs = format_attribs(var)
        doc = inline_doc(var.doc_list, link_index) if hasattr(var, "doc_list") else ""

        if show_intent:
            intent = var.intent if hasattr(var, "intent") and var.intent else ""
            lines.append(f"| {name} | {vtype} | {intent} | {attribs} | {doc} |")
        else:
            lines.append(f"| {name} | {vtype} | {attribs} | {doc} |")

    return "\n".join(lines)


def format_procedure(proc, link_index: Optional[dict] = None) -> str:
    """Format a subroutine or function section."""
    lines = []

    lines.append(f"### {proc.name}\n")

    doc = format_doc(proc.doc_list, link_index)
    if doc:
        lines.append(doc)
        lines.append("")

    if hasattr(proc, "attribs") and proc.attribs:
        attr_str = ", ".join(str(a) for a in proc.attribs)
        lines.append(f"**Attributes**: {attr_str}\n")

    arg_names = []
    for arg in proc.args:
        if hasattr(arg, "name"):
            arg_names.append(arg.name)
        else:
            arg_names.append(str(arg))

    proc_kind = proc.proctype.lower() if hasattr(proc, "proctype") else "subroutine"
    sig = f"{proc_kind} {proc.name}({', '.join(arg_names)})"

    if hasattr(proc, "retvar") and proc.retvar:
        retvar = proc.retvar
        ret_type = format_type_str(retvar, link_index)
        if retvar.name != proc.name:
            sig += f" result({retvar.name})"
        if link_index and "[" in ret_type:
            lines.append(f"**Returns**: {ret_type}\n")
        else:
            lines.append(f"**Returns**: `{ret_type}`\n")

    lines.append(f"```fortran\n{sig}\n```\n")

    real_args = [a for a in proc.args if hasattr(a, "name")]
    if real_args:
        lines.append("**Arguments**\n")
        lines.append(format_variable_table(real_args, show_intent=True, link_index=link_index))
        lines.append("")

    return "\n".join(lines)


def format_bound_proc_table(boundprocs: list, link_index: Optional[dict] = None) -> str:
    """Generate a Markdown table for type-bound procedures."""
    if not boundprocs:
        return ""

    lines = [
        "| Name | Attributes | Description |",
        "|------|------------|-------------|",
    ]

    for bp in boundprocs:
        name = f"`{bp.name}`"
        attribs = escape_pipe(", ".join(str(a) for a in bp.attribs)) if bp.attribs else ""
        doc = inline_doc(bp.doc_list, link_index) if hasattr(bp, "doc_list") else ""
        lines.append(f"| {name} | {attribs} | {doc} |")

    return "\n".join(lines)


def format_type(dtype, link_index: Optional[dict] = None) -> str:
    """Format a derived type section."""
    lines = []

    lines.append(f"### {dtype.name}\n")

    doc = format_doc(dtype.doc_list, link_index)
    if doc:
        lines.append(doc)
        lines.append("")

    if dtype.extends:
        extends_name = dtype.extends.name if hasattr(dtype.extends, "name") else str(dtype.extends)
        if link_index:
            url = link_index.get(extends_name.lower())
            if url:
                lines.append(f"**Extends**: [`{extends_name}`]({url})\n")
            else:
                lines.append(f"**Extends**: `{extends_name}`\n")
        else:
            lines.append(f"**Extends**: `{extends_name}`\n")

    if hasattr(dtype, "attribs") and dtype.attribs:
        lines.append(f"**Attributes**: {', '.join(str(a) for a in dtype.attribs)}\n")

    if dtype.variables:
        lines.append("#### Components\n")
        lines.append(format_variable_table(dtype.variables, link_index=link_index))
        lines.append("")

    if dtype.boundprocs:
        lines.append("#### Type-Bound Procedures\n")
        lines.append(format_bound_proc_table(dtype.boundprocs, link_index))
        lines.append("")

    return "\n".join(lines)


def format_interface(iface, link_index: Optional[dict] = None) -> str:
    """Format an interface section."""
    lines = []
    lines.append(f"### {iface.name}\n")

    doc = format_doc(iface.doc_list, link_index)
    if doc:
        lines.append(doc)
        lines.append("")

    subs = list(iface.subroutines) if hasattr(iface, "subroutines") else []
    funcs = list(iface.functions) if hasattr(iface, "functions") else []
    if not subs and not funcs and hasattr(iface, "routines"):
        procs = list(iface.routines)
    else:
        procs = subs + funcs
    if procs:
        for proc in procs:
            lines.append(format_procedure(proc, link_index))
    elif hasattr(iface, "modprocs") and iface.modprocs:
        names = [str(mp.name) if hasattr(mp, "name") else str(mp) for mp in iface.modprocs]
        if link_index:
            linked = []
            for n in names:
                url = link_index.get(n.lower())
                if url:
                    linked.append(f"[`{n}`]({url})")
                else:
                    linked.append(f"`{n}`")
            lines.append(f"**Module procedures**: {', '.join(linked)}\n")
        else:
            lines.append(f"**Module procedures**: {', '.join(f'`{n}`' for n in names)}\n")

    return "\n".join(lines)


def format_module(
    module,
    src_root: Optional[str] = None,
    link_index: Optional[dict] = None,
) -> str:
    """Generate a full Markdown page for a module.

    Args:
        module: A FORD FortranModule object.
        src_root: Optional root path to strip for relative source paths.
        link_index: Optional name→URL mapping from :func:`build_entity_index`
                    used to resolve ``[[name]]`` cross-references.

    Returns:
        A string containing the complete Markdown page content.
    """
    lines = []

    lines.append("---")
    lines.append(f"title: {module.name}")
    lines.append("---")
    lines.append("")

    lines.append(f"# {module.name}\n")

    doc = format_doc(module.doc_list, link_index)
    if doc:
        lines.append(f"> {doc}\n")

    src_path = get_source_path(module, src_root)
    if src_path:
        lines.append(f"**Source**: `{src_path}`\n")

    toc_items = []
    for dtype in module.types:
        toc_items.append(f"- [{dtype.name}](#{slugify(dtype.name)})")
    for iface in module.interfaces:
        toc_items.append(f"- [{iface.name}](#{slugify(iface.name)})")
    for sub in (module.subroutines or []):
        toc_items.append(f"- [{sub.name}](#{slugify(sub.name)})")
    for func in (module.functions or []):
        toc_items.append(f"- [{func.name}](#{slugify(func.name)})")
    if toc_items:
        lines.append("## Contents\n")
        lines.extend(toc_items)
        lines.append("")

    if module.variables:
        lines.append("## Variables\n")
        lines.append(format_variable_table(module.variables, link_index=link_index))
        lines.append("")

    if module.types:
        lines.append("## Derived Types\n")
        for dtype in module.types:
            lines.append(format_type(dtype, link_index))

    if module.interfaces:
        lines.append("## Interfaces\n")
        for iface in module.interfaces:
            lines.append(format_interface(iface, link_index))

    subs = list(module.subroutines) if module.subroutines else []
    if subs:
        lines.append("## Subroutines\n")
        for sub in subs:
            lines.append(format_procedure(sub, link_index))

    funcs = list(module.functions) if module.functions else []
    if funcs:
        lines.append("## Functions\n")
        for func in funcs:
            lines.append(format_procedure(func, link_index))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sidebar generation
# ---------------------------------------------------------------------------

def generate_sidebar(modules: list, src_root: Optional[str] = None) -> list:
    """Generate VitePress sidebar items grouped by source directory structure.

    Modules are grouped by the first two path components under the source root
    (e.g. 'app/nasto', 'lib/common'). Group names are title-cased.

    Args:
        modules: List of FORD FortranModule objects.
        src_root: Optional root path for relative path computation.

    Returns:
        A list of sidebar group dicts suitable for VitePress config.
    """
    groups: dict[str, list[str]] = {}

    for module in modules:
        path = get_source_path(module, src_root)
        group = _classify_module(path)
        groups.setdefault(group, []).append(module.name)

    sidebar_items = []
    for group_name in sorted(groups.keys()):
        items = sorted(groups[group_name])
        sidebar_items.append({
            "text": group_name,
            "collapsed": True,
            "items": [{"text": name, "link": f"/api/{name}"} for name in items],
        })

    return sidebar_items


def _classify_module(path: str) -> str:
    """Classify a module into a sidebar group based on its source path.

    Recognizes common Fortran project layouts:
      - src/app/<name>/...  -> 'Applications / NAME'
      - src/lib/<name>/...  -> 'Library / name'
      - src/<name>/...      -> 'name'
      - anything else       -> 'Other'
    """
    parts = Path(path).parts

    # Find 'src' in path and work from there
    try:
        src_idx = list(parts).index("src")
        after_src = parts[src_idx + 1:]
    except ValueError:
        # No 'src' directory -- use first two components
        after_src = parts[:2] if len(parts) >= 2 else parts

    if len(after_src) >= 2:
        category = after_src[0].lower()
        name = after_src[1]
        if category == "app":
            return f"Applications / {name.upper()}"
        elif category == "lib":
            return f"Library / {name}"
        else:
            return f"{category} / {name}"
    elif len(after_src) == 1:
        return after_src[0]

    return "Other"


# ---------------------------------------------------------------------------
# Main generation entry point
# ---------------------------------------------------------------------------

def generate(
    project_file: Path,
    output_dir: Path,
    api_prefix: str = "/api/",
    src_root: Optional[str] = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Generate VitePress API documentation from a FORD project file.

    This is the main entry point for programmatic usage.

    Args:
        project_file: Path to FORD project file (.md with metadata header).
        output_dir: Directory to write generated .md files into.
        api_prefix: URL prefix for API links in sidebar (default: '/api/').
        src_root: Root path to strip from source file paths. If None, auto-detected.
        verbose: Print progress to stdout.

    Returns:
        A dict with keys: 'modules' (count), 'files' (list of written paths),
        'sidebar' (the sidebar data structure).
    """
    if verbose:
        print(f"Loading FORD project from {project_file}...")

    project = load_project(project_file)
    modules = sorted(project.modules, key=lambda m: m.name)

    if verbose:
        print(f"Found {len(modules)} modules")

    link_index = build_entity_index(project, api_prefix)

    output_dir.mkdir(parents=True, exist_ok=True)
    written_files = []

    # Generate per-module pages
    for module in modules:
        md = format_module(module, src_root=src_root, link_index=link_index)
        out_file = output_dir / f"{module.name}.md"
        out_file.write_text(md, encoding="utf-8")
        written_files.append(out_file)
        if verbose:
            print(f"  -> {out_file}")

    # Generate sidebar JSON
    sidebar = generate_sidebar(modules, src_root=src_root)

    # Rewrite links with custom prefix if not default
    if api_prefix != "/api/":
        for group in sidebar:
            for item in group["items"]:
                item["link"] = api_prefix + item["link"].split("/api/")[-1]

    sidebar_file = output_dir / "_sidebar.json"
    sidebar_file.write_text(json.dumps(sidebar, indent=2), encoding="utf-8")
    written_files.append(sidebar_file)
    if verbose:
        print(f"  -> {sidebar_file}")

    # Generate index page
    index_lines = [
        "---",
        "title: API Reference",
        "---",
        "",
        "# API Reference",
        "",
        "Auto-generated from Fortran source doc comments using [FORMAL](https://github.com/szaghi/formal).",
        "",
    ]
    for group in sidebar:
        index_lines.append(f"## {group['text']}\n")
        for item in group["items"]:
            index_lines.append(f"- [{item['text']}]({item['link']})")
        index_lines.append("")

    index_file = output_dir / "index.md"
    index_file.write_text("\n".join(index_lines), encoding="utf-8")
    written_files.append(index_file)
    if verbose:
        print(f"  -> {index_file}")
        print(f"\nDone! Generated {len(modules)} module pages in {output_dir}/")

    return {
        "modules": len(modules),
        "files": written_files,
        "sidebar": sidebar,
    }
