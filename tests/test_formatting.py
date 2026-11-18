"""Unit tests for pure text formatting functions in formal.generator."""

import pytest
from formal.generator import (
    strip_html,
    escape_pipe,
    format_doc,
    inline_doc,
    format_type_str,
    format_attribs,
    build_entity_index,
    resolve_links,
    linkify_type_str,
    slugify,
    format_call_diagram,
)
from mocks import MockVariable, MockModule, MockType, MockProcedure, MockInterface, MockProject


# ---------------------------------------------------------------------------
# strip_html
# ---------------------------------------------------------------------------

class TestStripHtml:
    def test_removes_anchor_tag(self):
        assert strip_html('<a href="foo.html">bar</a>') == "bar"

    def test_removes_br(self):
        assert strip_html("hello<br/>world") == "helloworld"

    def test_removes_nested_tags(self):
        assert strip_html("<b><i>text</i></b>") == "text"

    def test_no_tags(self):
        assert strip_html("plain text") == "plain text"

    def test_empty_string(self):
        assert strip_html("") == ""

    def test_self_closing_tag(self):
        assert strip_html("before<br />after") == "beforeafter"


# ---------------------------------------------------------------------------
# escape_pipe
# ---------------------------------------------------------------------------

class TestEscapePipe:
    def test_escapes_pipe(self):
        assert escape_pipe("a|b") == r"a\|b"

    def test_no_pipe(self):
        assert escape_pipe("abc") == "abc"

    def test_multiple_pipes(self):
        assert escape_pipe("|a|b|") == r"\|a\|b\|"

    def test_empty_string(self):
        assert escape_pipe("") == ""


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_lowercase(self):
        assert slugify("MyType") == "mytype"

    def test_underscore_becomes_hyphen(self):
        assert slugify("strf_r8p") == "strf-r8p"

    def test_multiple_underscores(self):
        assert slugify("my_long_name") == "my-long-name"

    def test_no_underscores_unchanged(self):
        assert slugify("mytype") == "mytype"

    def test_mixed_case_and_underscores(self):
        assert slugify("My_Type") == "my-type"

    def test_already_hyphenated(self):
        assert slugify("my-type") == "my-type"

    def test_consecutive_underscores_single_hyphen(self):
        assert slugify("a__b") == "a-b"


# ---------------------------------------------------------------------------
# format_doc
# ---------------------------------------------------------------------------

class TestFormatDoc:
    def test_empty_list(self):
        assert format_doc([]) == ""

    def test_single_line(self):
        assert format_doc(["Hello world."]) == "Hello world."

    def test_multiple_lines(self):
        assert format_doc(["Line 1", "Line 2"]) == "Line 1\nLine 2"

    def test_strips_outer_whitespace(self):
        assert format_doc(["  hello  ", "  world  "]) == "hello  \n  world"

    def test_whitespace_only_list(self):
        assert format_doc(["  ", "  "]) == ""


# ---------------------------------------------------------------------------
# inline_doc
# ---------------------------------------------------------------------------

class TestInlineDoc:
    def test_empty_list(self):
        assert inline_doc([]) == ""

    def test_single_line(self):
        assert inline_doc(["The doc."]) == "The doc."

    def test_returns_first_nonempty(self):
        assert inline_doc(["", "  ", "Real doc"]) == "Real doc"

    def test_strips_html(self):
        assert inline_doc(['<a href="x">link</a> text']) == "link text"

    def test_escapes_pipes(self):
        assert inline_doc(["a|b"]) == r"a\|b"

    def test_all_whitespace(self):
        assert inline_doc(["", "  ", ""]) == ""

    def test_joins_wrapped_first_paragraph(self):
        assert inline_doc(["The state of the stage; null when", " the state is q.", "", "Second."]) == (
            "The state of the stage; null when the state is q.")

    def test_stops_at_list(self):
        assert inline_doc(["A field, in one of two layouts:", "+ `V_FIRST`", "+ `V_LAST`"]) == (
            "A field, in one of two layouts:")

    def test_stops_at_table_and_fence(self):
        assert inline_doc(["Kernels:", "| a | b |"]) == "Kernels:"
        assert inline_doc(["Example:", "```fortran", "x = 1", "```"]) == "Example:"


# ---------------------------------------------------------------------------
# format_type_str
# ---------------------------------------------------------------------------

class TestFormatTypeStr:
    def test_uses_full_type(self):
        var = MockVariable(full_type="real(real64)")
        assert format_type_str(var) == "real(real64)"

    def test_strips_html_from_full_type(self):
        var = MockVariable(full_type='<a href="x">integer</a>')
        assert format_type_str(var) == "integer"

    def test_fallback_to_vartype(self):
        var = MockVariable(vartype="integer", full_type="")
        assert format_type_str(var) == "integer"

    def test_vartype_with_kind(self):
        var = MockVariable(vartype="real", kind="dp", full_type="")
        assert format_type_str(var) == "real(dp)"

    def test_escapes_pipe_in_type(self):
        var = MockVariable(full_type="type(a|b)")
        assert format_type_str(var) == r"type(a\|b)"

    def test_empty_type(self):
        var = MockVariable(vartype="", full_type="")
        assert format_type_str(var) == ""


# ---------------------------------------------------------------------------
# format_attribs
# ---------------------------------------------------------------------------

class TestFormatAttribs:
    def test_empty(self):
        var = MockVariable(attribs=[])
        assert format_attribs(var) == ""

    def test_single_attrib(self):
        var = MockVariable(attribs=["allocatable"])
        assert format_attribs(var) == "allocatable"

    def test_multiple_attribs(self):
        var = MockVariable(attribs=["dimension(:)", "intent(in)"])
        assert format_attribs(var) == "dimension(:), intent(in)"

    def test_optional_flag(self):
        var = MockVariable(optional=True)
        assert format_attribs(var) == "optional"

    def test_parameter_flag(self):
        var = MockVariable(parameter=True)
        assert format_attribs(var) == "parameter"

    def test_combined(self):
        var = MockVariable(attribs=["allocatable"], optional=True, parameter=True)
        assert format_attribs(var) == "allocatable, optional, parameter"

    def test_escapes_pipe(self):
        var = MockVariable(attribs=["a|b"])
        assert format_attribs(var) == r"a\|b"


# ---------------------------------------------------------------------------
# build_entity_index
# ---------------------------------------------------------------------------

class TestBuildEntityIndex:
    def _make_project(self):
        mod = MockModule(
            name="my_module",
            types=[MockType(name="MyType")],
            subroutines=[MockProcedure(name="my_sub", proctype="subroutine")],
            functions=[MockProcedure(name="my_func", proctype="function")],
            interfaces=[MockInterface(name="my_iface")],
        )
        return MockProject(modules=[mod])

    def test_module_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_module"] == "/api/my_module"

    def test_type_indexed_bare(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["mytype"] == "/api/my_module#mytype"

    def test_type_indexed_compound(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_module:mytype"] == "/api/my_module#mytype"

    def test_subroutine_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_sub"] == "/api/my_module#my-sub"

    def test_function_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_func"] == "/api/my_module#my-func"

    def test_interface_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_iface"] == "/api/my_module#my-iface"

    def test_compound_proc_key(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_module:my_sub"] == "/api/my_module#my-sub"

    def test_custom_api_prefix(self):
        project = self._make_project()
        index = build_entity_index(project, api_prefix="/docs/api/")
        assert index["my_module"] == "/docs/api/my_module"
        assert index["mytype"] == "/docs/api/my_module#mytype"

    def test_empty_project(self):
        project = MockProject(modules=[])
        index = build_entity_index(project)
        assert index == {}

    def test_keys_are_lowercase(self):
        mod = MockModule(name="UpperMod", types=[MockType(name="BigType")])
        project = MockProject(modules=[mod])
        index = build_entity_index(project)
        assert "uppermod" in index
        assert "bigtype" in index

    def test_variables_indexed_to_module_page(self):
        var = MockVariable(name="I4P")
        mod = MockModule(name="penf_global", variables=[var])
        project = MockProject(modules=[mod])
        index = build_entity_index(project)
        assert index["i4p"] == "/api/penf_global#variables"

    def test_variable_url_is_the_variables_section(self):
        var = MockVariable(name="R8P")
        mod = MockModule(name="penf_global", variables=[var])
        project = MockProject(modules=[mod])
        index = build_entity_index(project)
        assert index["r8p"].endswith("#variables")


# ---------------------------------------------------------------------------
# resolve_links
# ---------------------------------------------------------------------------

class TestResolveLinks:
    def _index(self):
        return {
            "my_module": "/api/my_module",
            "mytype": "/api/my_module#mytype",
            "my_sub": "/api/my_module#my_sub",
            "my_module:mytype": "/api/my_module#mytype",
            "my_module:my_sub": "/api/my_module#my_sub",
        }

    def test_bare_name_resolved(self):
        result = resolve_links("See [[my_sub]] for details.", self._index())
        assert result == "See [my_sub](/api/my_module#my_sub) for details."

    def test_qualified_name_resolved(self):
        result = resolve_links("Use [[my_module:mytype]] here.", self._index())
        assert result == "Use [mytype](/api/my_module#mytype) here."

    def test_unknown_name_becomes_plain_text(self):
        result = resolve_links("See [[missing_thing]] now.", self._index())
        assert result == "See missing_thing now."

    def test_case_insensitive_lookup(self):
        result = resolve_links("[[MY_SUB]] is useful.", self._index())
        assert result == "[MY_SUB](/api/my_module#my_sub) is useful."

    def test_module_link(self):
        result = resolve_links("Defined in [[my_module]].", self._index())
        assert result == "Defined in [my_module](/api/my_module)."

    def test_no_markers(self):
        text = "Plain text without any markers."
        assert resolve_links(text, self._index()) == text

    def test_multiple_markers(self):
        result = resolve_links("[[my_sub]] calls [[mytype]].", self._index())
        assert result == "[my_sub](/api/my_module#my_sub) calls [mytype](/api/my_module#mytype)."

    def test_qualified_fallback_to_child_bare(self):
        # [[unknown_mod:my_sub]] — compound key missing, falls back to child bare key
        result = resolve_links("[[unknown_mod:my_sub]] is here.", self._index())
        assert result == "[my_sub](/api/my_module#my_sub) is here."

    def test_empty_string(self):
        assert resolve_links("", self._index()) == ""

    def test_format_doc_with_link_index(self):
        index = self._index()
        result = format_doc(["See [[my_sub]] for details."], link_index=index)
        assert result == "See [my_sub](/api/my_module#my_sub) for details."

    def test_format_doc_without_link_index_unchanged(self):
        result = format_doc(["See [[my_sub]] for details."])
        assert result == "See [[my_sub]] for details."

    def test_inline_doc_with_link_index(self):
        index = self._index()
        result = inline_doc(["See [[my_sub]] here."], link_index=index)
        assert result == "See [my_sub](/api/my_module#my_sub) here."


# ---------------------------------------------------------------------------
# linkify_type_str
# ---------------------------------------------------------------------------

class TestLinkifyTypeStr:
    def _index(self):
        return {
            "mytype": "/api/my_module#mytype",
            "mybase": "/api/my_module#mybase",
            "i4p": "/api/penf_global",
            "r8p": "/api/penf_global",
        }

    def test_type_paren_known(self):
        result = linkify_type_str("type(MyType)", self._index())
        assert result == "type([MyType](/api/my_module#mytype))"

    def test_class_paren_known(self):
        result = linkify_type_str("class(MyBase)", self._index())
        assert result == "class([MyBase](/api/my_module#mybase))"

    def test_kind_eq_known(self):
        result = linkify_type_str("integer(kind=I4P)", self._index())
        assert result == "integer(kind=[I4P](/api/penf_global))"

    def test_type_paren_unknown(self):
        result = linkify_type_str("type(unknown_type)", self._index())
        assert result == "type(unknown_type)"

    def test_kind_eq_unknown(self):
        result = linkify_type_str("real(kind=dp)", self._index())
        assert result == "real(kind=dp)"

    def test_multiple_matches(self):
        result = linkify_type_str("type(MyType), intent(in)", self._index())
        assert "type([MyType]" in result
        assert "intent(in)" in result

    def test_no_match_unchanged(self):
        text = "integer"
        assert linkify_type_str(text, self._index()) == text

    def test_case_insensitive_type(self):
        result = linkify_type_str("TYPE(MyType)", self._index())
        assert "[MyType]" in result

    def test_case_insensitive_kind(self):
        result = linkify_type_str("real(KIND=I4P)", self._index())
        assert "[I4P]" in result


# ---------------------------------------------------------------------------
# format_type_str with link_index
# ---------------------------------------------------------------------------

class TestFormatTypeStrWithLinkIndex:
    def _index(self):
        return {
            "mytype": "/api/my_module#mytype",
            "i4p": "/api/penf_global",
        }

    def test_type_paren_linked(self):
        var = MockVariable(full_type="type(MyType)")
        result = format_type_str(var, self._index())
        assert result == "type([MyType](/api/my_module#mytype))"

    def test_kind_eq_linked(self):
        var = MockVariable(full_type="integer(kind=I4P)")
        result = format_type_str(var, self._index())
        assert result == "integer(kind=[I4P](/api/penf_global))"

    def test_no_link_index_unchanged(self):
        var = MockVariable(full_type="type(MyType)")
        result = format_type_str(var)
        assert result == "type(MyType)"

    def test_unknown_name_no_link(self):
        var = MockVariable(full_type="type(UnknownType)")
        result = format_type_str(var, self._index())
        assert result == "type(UnknownType)"

    def test_pipe_still_escaped_after_linkify(self):
        var = MockVariable(full_type="type(a|b)")
        result = format_type_str(var, self._index())
        assert r"a\|b" in result


# ---------------------------------------------------------------------------
# format_call_diagram
# ---------------------------------------------------------------------------

class TestFormatCallDiagram:
    """The call graph: left to right, the procedure marked by the theme-neutral class `focus`."""

    @staticmethod
    def _proc(name, calls=()):
        from types import SimpleNamespace
        return SimpleNamespace(name=name, calls=[SimpleNamespace(name=c) for c in calls])

    def test_no_relations_empty(self):
        assert format_call_diagram(self._proc("lonely"), {}) == ""

    def test_left_to_right(self):
        out = format_call_diagram(self._proc("p", calls=["q"]), {})
        assert out.splitlines()[1] == "flowchart LR"

    def test_callers_in_callees_out(self):
        out = format_call_diagram(self._proc("p", calls=["q"]), {"p": ["a"]})
        assert '  a["a"] --> p["p"]' in out
        assert '  p["p"] --> q["q"]' in out

    def test_focus_class_without_colours(self):
        out = format_call_diagram(self._proc("p", calls=["q"]), {})
        assert "  class p focus" in out
        classdef = [ln for ln in out.splitlines() if ln.strip().startswith("classDef focus")]
        assert len(classdef) == 1
        # no fill, stroke colour or text colour: the node keeps the contrast of the rendering theme
        assert "fill" not in classdef[0] and "color" not in classdef[0] and "stroke:" not in classdef[0]
        assert "style " not in out

    def test_wide_fan_stays_three_columns(self):
        callers = {"c": [f"caller_{i}" for i in range(8)]}
        out = format_call_diagram(self._proc("c"), callers)
        assert out.splitlines()[1] == "flowchart LR"
        assert sum("--> c[" in ln for ln in out.splitlines()) == 8


# ---------------------------------------------------------------------------
# re-exports of a facade module
# ---------------------------------------------------------------------------

class TestReexports:
    def _facade(self):
        from mocks import MockType
        lib = MockModule(name="lib")
        t = MockType(name="box", doc_list=["A box.", "More."], parent=lib)
        f = MockProcedure(name="box_interior", proctype="Function", doc_list=["Interior."], parent=lib)
        v = MockVariable(name="LAYOUT", doc_list=["Layout."], parameter=True)
        v.parent = lib
        facade = MockModule(name="facade")
        facade.public_list = ["box", "box_interior", "layout", "r_p", "i4p"]
        facade.pub_types = {"box": t}
        facade.pub_procs = {"box_interior": f}
        facade.pub_vars = {"layout": v}
        kinds = MockModule(name="kinds")
        kinds.public_list = ["r_p"]
        kinds.parent = type("F", (), {"raw_src": "module kinds\nuse penf, only : R_P\n"})()
        facade.uses = [lib, kinds, "penf"]
        facade.parent = type("F", (), {"raw_src": "module facade\nuse penf, only : I4P, &\n  & I8P\nuse kinds\n"})()
        return facade

    def test_rows_in_public_order_linked(self):
        from formal.generator import format_reexports
        index = {"lib": "/api/lib", "lib:box": "/api/lib#box", "lib:box_interior": "/api/lib#box-interior",
                 "lib:layout": "/api/lib#variables", "kinds": "/api/kinds"}
        out = format_reexports(self._facade(), index).splitlines()
        assert out[2] == "| [`box`](/api/lib#box) | type | [lib](/api/lib) | A box. More. |"
        assert out[3] == "| [`box_interior`](/api/lib#box-interior) | function | [lib](/api/lib) | Interior. |"
        assert out[4].startswith("| [`LAYOUT`](/api/lib#variables) | parameter |")

    def test_unresolved_traced_to_their_module(self):
        from formal.generator import format_reexports
        out = format_reexports(self._facade(), {"kinds": "/api/kinds"})
        assert "| `R_P` |  | [kinds](/api/kinds) |  |" in out
        assert "| `I4P` |  | penf |  |" in out

    def test_own_entities_not_listed(self):
        from formal.generator import format_reexports
        mod = MockModule(name="lib")
        p = MockProcedure(name="f", parent=mod)
        mod.public_list = ["f"]
        mod.pub_procs = {"f": p}
        assert format_reexports(mod) == ""


# ---------------------------------------------------------------------------
# diagram nodes as links
# ---------------------------------------------------------------------------

class TestDiagramLinks:
    def test_relative_href(self):
        from formal.generator import relative_href
        page = "/api/src/lib/selah_stepper"
        assert relative_href("/api/src/lib/selah_box", page) == "selah_box.html"
        assert relative_href("/api/src/lib/selah_box#box", page) == "selah_box.html#box"
        assert relative_href("/api/src/lib/selah_stepper#stepper", page) == "#stepper"
        assert relative_href("/api/other", page) == "../../other.html"
        assert relative_href("/api/a", "/api/b") == "a.html"

    def test_dependency_nodes_link(self):
        from types import SimpleNamespace
        from formal.generator import format_dependency_diagram
        mod = SimpleNamespace(name="m", uses=[SimpleNamespace(name="dep"), SimpleNamespace(name="ext")])
        out = format_dependency_diagram(mod, link_index={"m": "/api/m", "dep": "/api/dep"}, page_url="/api/m")
        assert '  click dep href "dep.html" "dep"' in out
        assert "click ext" not in out
        assert "click m " not in out

    def test_no_links_without_page(self):
        from types import SimpleNamespace
        from formal.generator import format_dependency_diagram
        mod = SimpleNamespace(name="m", uses=[SimpleNamespace(name="dep")])
        assert "click" not in format_dependency_diagram(mod, link_index={"dep": "/api/dep"})

    def test_call_graph_nodes_link_not_focus(self):
        from types import SimpleNamespace
        p = SimpleNamespace(name="p", calls=[SimpleNamespace(name="q", parent=SimpleNamespace(name="other"))])
        index = {"a": "/api/m#a", "q": "/api/x#q", "other:q": "/api/other#q", "p": "/api/m#p"}
        out = format_call_diagram(p, {"p": ["a"]}, link_index=index, page_url="/api/m")
        assert '  click a href "#a" "a"' in out
        assert '  click q href "other.html#q" "q"' in out
        assert "click p " not in out

    def test_inheritance_nodes_link(self):
        from formal.generator import format_inheritance_diagram
        parent = MockType(name="base")
        child = MockType(name="mid", extends=parent)
        out = format_inheritance_diagram(child, {"mid": ["leaf"]},
                                         link_index={"base": "/api/b#base", "leaf": "/api/m#leaf"}, page_url="/api/m")
        assert '  click base href "b.html#base" "base"' in out
        assert '  click leaf href "#leaf" "leaf"' in out


# ---------------------------------------------------------------------------
# the API index page
# ---------------------------------------------------------------------------

class TestFormatIndex:
    SIDEBAR = [{"text": "src/lib", "collapsed": True, "items": [{"text": "m", "link": "/api/src/lib/m"}]}]

    def test_without_intro(self):
        from formal.generator import format_index
        out = format_index(self.SIDEBAR)
        assert out.startswith("---\ntitle: API Reference\n---\n\n# API Reference\n\nAuto-generated")
        assert "## src/lib\n\n- [m](/api/src/lib/m)" in out

    def test_intro_before_modules_links_resolved(self):
        from formal.generator import format_index
        out = format_index(self.SIDEBAR, "Start with [[m]].\n\n## Layers", {"m": "/api/src/lib/m"})
        assert "# API Reference\n\nStart with [m](/api/src/lib/m).\n\n## Layers\n" in out
        assert out.index("## Layers") < out.index("## src/lib")
