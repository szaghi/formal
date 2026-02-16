"""Unit tests for _classify_module sidebar grouping."""

import pytest
from formal.generator import _classify_module


class TestClassifyModule:
    def test_app_nasto(self):
        assert _classify_module("src/app/nasto/foo.F90") == "Applications / NASTO"

    def test_app_prism(self):
        assert _classify_module("src/app/prism/common/bar.F90") == "Applications / PRISM"

    def test_lib_common(self):
        assert _classify_module("src/lib/common/bar.F90") == "Library / common"

    def test_lib_fnl(self):
        assert _classify_module("src/lib/fnl/baz.F90") == "Library / fnl"

    def test_tests_dir(self):
        assert _classify_module("src/tests/something/test.F90") == "tests / something"

    def test_no_src_prefix(self):
        # No 'src' in path → uses first two components; 'lib' triggers Library grouping
        assert _classify_module("lib/foo/bar.F90") == "Library / foo"

    def test_standalone_file(self):
        # Single file, no directory structure → single element returned
        assert _classify_module("standalone.F90") == "standalone.F90"

    def test_deep_nested_app(self):
        assert _classify_module("src/app/chase/cpu/main.F90") == "Applications / CHASE"

    def test_src_with_absolute_path(self):
        result = _classify_module("/home/user/project/src/lib/nvf/mod.F90")
        assert result == "Library / nvf"

    def test_src_single_level(self):
        # src/<name>/file.F90 with only one level after src
        result = _classify_module("src/utils/helper.F90")
        assert result == "utils / helper.F90"

    def test_src_single_dir_only(self):
        # src/<name> with nothing after → single element
        result = _classify_module("src/utils")
        assert result == "utils"
