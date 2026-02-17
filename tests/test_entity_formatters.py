"""Unit tests for entity formatting functions using mock objects."""

import pytest
from formal.generator import (
    format_variable_table,
    format_procedure,
    format_bound_proc_table,
    format_type,
    format_interface,
    format_module,
)
from mocks import (
    MockVariable,
    MockProcedure,
    MockBoundProc,
    MockType,
    MockInterface,
    MockModule,
    MockModProc,
    MockParent,
)


# ---------------------------------------------------------------------------
# format_variable_table
# ---------------------------------------------------------------------------

class TestFormatVariableTable:
    def test_empty_list(self):
        assert format_variable_table([]) == ""

    def test_single_variable_no_intent(self):
        var = MockVariable(name="density", vartype="real", kind="rp", full_type="real(rp)", doc_list=["Fluid density."])
        result = format_variable_table([var])
        assert "| `density` |" in result
        assert "real(rp)" in result
        assert "Fluid density." in result
        # No intent column
        assert "Intent" not in result

    def test_with_intent(self):
        var = MockVariable(name="n", vartype="integer", full_type="integer", intent="in", doc_list=["Count."])
        result = format_variable_table([var], show_intent=True)
        assert "| Intent |" in result
        assert "| in |" in result

    def test_pipe_in_type(self):
        var = MockVariable(name="x", full_type="type(a|b)")
        result = format_variable_table([var])
        assert r"a\|b" in result

    def test_multiple_variables(self):
        v1 = MockVariable(name="x", full_type="real")
        v2 = MockVariable(name="y", full_type="integer")
        result = format_variable_table([v1, v2])
        assert "`x`" in result
        assert "`y`" in result

    def test_variable_with_attribs(self):
        var = MockVariable(name="arr", full_type="real", attribs=["allocatable", "dimension(:)"])
        result = format_variable_table([var])
        assert "allocatable" in result
        assert "dimension(:)" in result


# ---------------------------------------------------------------------------
# format_procedure
# ---------------------------------------------------------------------------

class TestFormatProcedure:
    def test_subroutine_basic(self):
        args = [MockVariable(name="x", intent="in", full_type="real")]
        proc = MockProcedure(name="compute", proctype="subroutine", args=args, doc_list=["Do computation."])
        result = format_procedure(proc)
        assert "### compute" in result
        assert "Do computation." in result
        assert "subroutine compute(x)" in result
        assert "**Arguments**" in result

    def test_function_with_retvar(self):
        args = [MockVariable(name="n", intent="in", full_type="integer")]
        retvar = MockVariable(name="res", full_type="real(rp)")
        proc = MockProcedure(name="factorial", proctype="function", args=args, retvar=retvar)
        result = format_procedure(proc)
        assert "function factorial(n)" in result
        assert "result(res)" in result
        assert "**Returns**: `real(rp)`" in result

    def test_function_retvar_linked_drops_backticks(self):
        retvar = MockVariable(name="res", full_type="type(MyType)")
        proc = MockProcedure(name="make_type", proctype="function", args=[], retvar=retvar)
        index = {"mytype": "/api/my_module#mytype"}
        result = format_procedure(proc, link_index=index)
        assert "**Returns**: type([MyType](/api/my_module#mytype))" in result
        # backtick wrapping removed when links are present
        assert "**Returns**: `" not in result

    def test_function_retvar_no_link_index_uses_backticks(self):
        retvar = MockVariable(name="res", full_type="type(MyType)")
        proc = MockProcedure(name="make_type", proctype="function", args=[], retvar=retvar)
        result = format_procedure(proc)
        assert "**Returns**: `type(MyType)`" in result

    def test_function_retvar_same_name(self):
        retvar = MockVariable(name="myfunc", full_type="integer")
        proc = MockProcedure(name="myfunc", proctype="function", args=[], retvar=retvar)
        result = format_procedure(proc)
        # Should NOT show result() clause when names match
        assert "result(" not in result
        assert "**Returns**: `integer`" in result

    def test_procedure_with_attribs(self):
        proc = MockProcedure(name="sub", attribs=["pure", "elemental"], args=[])
        result = format_procedure(proc)
        assert "**Attributes**: pure, elemental" in result

    def test_no_args(self):
        proc = MockProcedure(name="init", args=[], doc_list=["Initialize."])
        result = format_procedure(proc)
        assert "subroutine init()" in result
        assert "**Arguments**" not in result


# ---------------------------------------------------------------------------
# format_bound_proc_table
# ---------------------------------------------------------------------------

class TestFormatBoundProcTable:
    def test_empty(self):
        assert format_bound_proc_table([]) == ""

    def test_single_bound_proc(self):
        bp = MockBoundProc(name="init", attribs=["public"], doc_list=["Initialize."])
        result = format_bound_proc_table([bp])
        assert "| `init` |" in result
        assert "public" in result
        assert "Initialize." in result

    def test_no_attribs(self):
        bp = MockBoundProc(name="run", attribs=[], doc_list=[])
        result = format_bound_proc_table([bp])
        assert "| `run` |" in result

    def test_multiple(self):
        bp1 = MockBoundProc(name="a", attribs=[], doc_list=["First."])
        bp2 = MockBoundProc(name="b", attribs=["deferred"], doc_list=["Second."])
        result = format_bound_proc_table([bp1, bp2])
        assert "`a`" in result
        assert "`b`" in result
        assert "deferred" in result


# ---------------------------------------------------------------------------
# format_type
# ---------------------------------------------------------------------------

class TestFormatType:
    def test_simple_type(self):
        var = MockVariable(name="n", full_type="integer", doc_list=["Count."])
        dtype = MockType(name="config_type", doc_list=["A configuration."], variables=[var])
        result = format_type(dtype)
        assert "### config_type" in result
        assert "A configuration." in result
        assert "#### Components" in result
        assert "`n`" in result

    def test_type_with_extends(self):
        parent = MockType(name="base_type")
        dtype = MockType(name="child_type", extends=parent, variables=[])
        result = format_type(dtype)
        assert "**Extends**: `base_type`" in result

    def test_type_extends_linked(self):
        parent = MockType(name="base_type")
        dtype = MockType(name="child_type", extends=parent, variables=[])
        index = {"base_type": "/api/my_module#base_type"}
        result = format_type(dtype, link_index=index)
        assert "**Extends**: [`base_type`](/api/my_module#base_type)" in result

    def test_type_extends_not_in_index(self):
        parent = MockType(name="external_base")
        dtype = MockType(name="child_type", extends=parent, variables=[])
        index = {}
        result = format_type(dtype, link_index=index)
        assert "**Extends**: `external_base`" in result

    def test_type_with_bound_procs(self):
        bp = MockBoundProc(name="init", doc_list=["Set up."])
        dtype = MockType(name="obj", boundprocs=[bp])
        result = format_type(dtype)
        assert "#### Type-Bound Procedures" in result
        assert "`init`" in result

    def test_empty_type(self):
        dtype = MockType(name="empty_type")
        result = format_type(dtype)
        assert "### empty_type" in result
        assert "Components" not in result
        assert "Type-Bound Procedures" not in result

    def test_type_with_attribs(self):
        dtype = MockType(name="abstract_type", attribs=["abstract"])
        result = format_type(dtype)
        assert "**Attributes**: abstract" in result


# ---------------------------------------------------------------------------
# format_interface
# ---------------------------------------------------------------------------

class TestFormatInterface:
    def test_interface_with_subroutines(self):
        sub = MockProcedure(name="sub1", args=[], doc_list=["A sub."])
        iface = MockInterface(name="generic_op", subroutines=[sub])
        result = format_interface(iface)
        assert "### generic_op" in result
        assert "### sub1" in result

    def test_interface_with_modprocs(self):
        mp1 = MockModProc(name="impl_a")
        mp2 = MockModProc(name="impl_b")
        iface = MockInterface(name="generic_call", modprocs=[mp1, mp2])
        result = format_interface(iface)
        assert "**Module procedures**" in result
        assert "`impl_a`" in result
        assert "`impl_b`" in result

    def test_interface_modprocs_linked(self):
        mp1 = MockModProc(name="digit_I8")
        mp2 = MockModProc(name="digit_I4")
        iface = MockInterface(name="digit", modprocs=[mp1, mp2])
        index = {
            "digit_i8": "/api/penf_stringify#digit_i8",
            "digit_i4": "/api/penf_stringify#digit_i4",
        }
        result = format_interface(iface, link_index=index)
        assert "[`digit_I8`](/api/penf_stringify#digit_i8)" in result
        assert "[`digit_I4`](/api/penf_stringify#digit_i4)" in result

    def test_interface_modprocs_partial_link(self):
        mp1 = MockModProc(name="known_proc")
        mp2 = MockModProc(name="unknown_proc")
        iface = MockInterface(name="generic", modprocs=[mp1, mp2])
        index = {"known_proc": "/api/mod#known_proc"}
        result = format_interface(iface, link_index=index)
        assert "[`known_proc`](/api/mod#known_proc)" in result
        assert "`unknown_proc`" in result
        assert "[`unknown_proc`]" not in result

    def test_interface_with_doc(self):
        iface = MockInterface(name="iface", doc_list=["Generic interface."])
        result = format_interface(iface)
        assert "Generic interface." in result

    def test_interface_routines_fallback(self):
        proc = MockProcedure(name="r1", args=[], doc_list=["Routine."])
        iface = MockInterface(name="generic", routines=[proc])
        result = format_interface(iface)
        assert "### r1" in result


# ---------------------------------------------------------------------------
# format_module
# ---------------------------------------------------------------------------

class TestFormatModule:
    def test_full_module(self):
        var = MockVariable(name="pi", full_type="real(rp)", parameter=True, doc_list=["Pi constant."])
        bp = MockBoundProc(name="init", doc_list=["Initialize."])
        comp = MockVariable(name="order", full_type="integer", doc_list=["Order."])
        dtype = MockType(name="config", doc_list=["Config type."], variables=[comp], boundprocs=[bp])
        sub = MockProcedure(name="setup", args=[], doc_list=["Setup routine."])
        func_ret = MockVariable(name="dt", full_type="real(rp)")
        func = MockProcedure(name="compute_dt", proctype="function", args=[], retvar=func_ret, doc_list=["Compute dt."])
        parent = MockParent(path="/home/user/project/src/lib/common/physics.F90")
        module = MockModule(
            name="physics_module",
            doc_list=["A physics module."],
            variables=[var],
            types=[dtype],
            subroutines=[sub],
            functions=[func],
            parent=parent,
        )
        result = format_module(module)
        assert "---\ntitle: physics_module\n---" in result
        assert "# physics_module" in result
        assert "> A physics module." in result
        assert "**Source**: `src/lib/common/physics.F90`" in result
        assert "## Variables" in result
        assert "`pi`" in result
        assert "## Derived Types" in result
        assert "### config" in result
        assert "## Subroutines" in result
        assert "### setup" in result
        assert "## Functions" in result
        assert "### compute_dt" in result

    def test_minimal_module(self):
        module = MockModule(name="empty_mod")
        result = format_module(module)
        assert "title: empty_mod" in result
        assert "# empty_mod" in result
        assert "## Variables" not in result
        assert "## Derived Types" not in result

    def test_module_with_interfaces(self):
        iface = MockInterface(name="generic_op", doc_list=["A generic."])
        module = MockModule(name="mod_iface", interfaces=[iface])
        result = format_module(module)
        assert "## Interfaces" in result
        assert "### generic_op" in result


# ---------------------------------------------------------------------------
# format_module TOC
# ---------------------------------------------------------------------------

class TestFormatModuleTOC:
    def test_toc_present_when_entities_exist(self):
        dtype = MockType(name="MyType")
        module = MockModule(name="my_mod", types=[dtype])
        result = format_module(module)
        assert "## Contents" in result
        assert "- [MyType](#mytype)" in result

    def test_toc_absent_for_empty_module(self):
        module = MockModule(name="empty_mod")
        result = format_module(module)
        assert "## Contents" not in result

    def test_toc_includes_all_entity_kinds(self):
        dtype = MockType(name="config_t")
        iface = MockInterface(name="generic_op")
        sub = MockProcedure(name="my_sub", proctype="subroutine", args=[])
        func = MockProcedure(name="my_func", proctype="function", args=[])
        module = MockModule(
            name="full_mod",
            types=[dtype],
            interfaces=[iface],
            subroutines=[sub],
            functions=[func],
        )
        result = format_module(module)
        assert "- [config_t](#config_t)" in result
        assert "- [generic_op](#generic_op)" in result
        assert "- [my_sub](#my_sub)" in result
        assert "- [my_func](#my_func)" in result

    def test_toc_anchor_is_lowercase(self):
        dtype = MockType(name="MyUpperType")
        module = MockModule(name="mod", types=[dtype])
        result = format_module(module)
        assert "- [MyUpperType](#myuppertype)" in result

    def test_toc_appears_before_entity_sections(self):
        dtype = MockType(name="config_t")
        module = MockModule(name="mod", types=[dtype])
        result = format_module(module)
        toc_pos = result.index("## Contents")
        types_pos = result.index("## Derived Types")
        assert toc_pos < types_pos
