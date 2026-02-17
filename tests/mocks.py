"""Lightweight mock classes that mimic FORD entity objects by duck-typing.

These match the attributes checked via hasattr in generator.py.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MockVariable:
    """Mock of a FORD FortranVariable."""
    name: str = "x"
    vartype: str = "real"
    kind: str = ""
    intent: str = ""
    attribs: list = field(default_factory=list)
    doc_list: list = field(default_factory=list)
    full_type: str = ""
    optional: bool = False
    parameter: bool = False


@dataclass
class MockProcedure:
    """Mock of a FORD FortranSubroutine/FortranFunction."""
    name: str = "my_sub"
    proctype: str = "subroutine"
    args: list = field(default_factory=list)
    doc_list: list = field(default_factory=list)
    attribs: list = field(default_factory=list)
    retvar: Optional[object] = None


@dataclass
class MockBoundProc:
    """Mock of a FORD BoundProcedure."""
    name: str = "bp"
    attribs: list = field(default_factory=list)
    doc_list: list = field(default_factory=list)


@dataclass
class MockType:
    """Mock of a FORD FortranType."""
    name: str = "my_type"
    doc_list: list = field(default_factory=list)
    extends: Optional[object] = None
    attribs: list = field(default_factory=list)
    variables: list = field(default_factory=list)
    boundprocs: list = field(default_factory=list)


@dataclass
class MockInterface:
    """Mock of a FORD FortranInterface."""
    name: str = "my_iface"
    doc_list: list = field(default_factory=list)
    subroutines: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    routines: list = field(default_factory=list)
    modprocs: list = field(default_factory=list)


@dataclass
class MockParent:
    """Mock of a FORD source file parent (has path attribute)."""
    path: str = "/home/user/project/src/lib/common/foo.F90"


@dataclass
class MockModule:
    """Mock of a FORD FortranModule."""
    name: str = "my_module"
    doc_list: list = field(default_factory=list)
    variables: list = field(default_factory=list)
    types: list = field(default_factory=list)
    interfaces: list = field(default_factory=list)
    subroutines: list = field(default_factory=list)
    functions: list = field(default_factory=list)
    parent: Optional[MockParent] = None
    filename: str = ""


@dataclass
class MockModProc:
    """Mock of a FORD module procedure reference."""
    name: str = "mp"


@dataclass
class MockProject:
    """Mock of a correlated FORD Project object."""
    modules: list = field(default_factory=list)
