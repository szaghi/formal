"""Unit tests for pure text formatting functions in formal.generator."""

import pytest
from formal.generator import (
    strip_html,
    escape_pipe,
    format_doc,
    inline_doc,
    format_type_str,
    format_attribs,
)
from mocks import MockVariable


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
