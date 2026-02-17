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
        assert index["my_sub"] == "/api/my_module#my_sub"

    def test_function_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_func"] == "/api/my_module#my_func"

    def test_interface_indexed(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_iface"] == "/api/my_module#my_iface"

    def test_compound_proc_key(self):
        project = self._make_project()
        index = build_entity_index(project)
        assert index["my_module:my_sub"] == "/api/my_module#my_sub"

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
        assert index["i4p"] == "/api/penf_global"

    def test_variable_url_has_no_anchor(self):
        var = MockVariable(name="R8P")
        mod = MockModule(name="penf_global", variables=[var])
        project = MockProject(modules=[mod])
        index = build_entity_index(project)
        assert "#" not in index["r8p"]


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
