"""End-to-end integration test: Fortran fixture -> FORD parse -> Markdown output.

These tests require FORD to be installed and functional.
Mark with @pytest.mark.integration so they can be skipped:
    pytest -m "not integration"
"""

import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def ford_available():
    """Check if FORD is importable."""
    try:
        import ford  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.integration


@pytest.mark.skipif(not ford_available(), reason="FORD not installed")
class TestFullPipeline:
    """Parse the sample_module.F90 fixture with FORD and generate Markdown."""

    def test_generate_from_fixture(self, tmp_path):
        from formal.scaffold import create_ford_project_file
        from formal.generator import generate

        fixture_src = FIXTURE_DIR / "sample_module.F90"
        assert fixture_src.exists(), f"Fixture not found: {fixture_src}"

        # Copy fixture to a src dir under tmp_path
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "sample_module.F90").write_text(fixture_src.read_text())

        # Create FORD project file
        ford_file = tmp_path / "doc" / "formal.md"
        create_ford_project_file(
            output_path=ford_file,
            project_name="TestProject",
            src_dirs=[str(src_dir)],
            docmark="<",
        )

        # Generate docs
        output_dir = tmp_path / "docs" / "api"
        result = generate(
            project_file=ford_file,
            output_dir=output_dir,
            verbose=False,
        )

        # Verify result dict
        assert result["modules"] >= 1
        assert len(result["files"]) >= 3  # module.md + _sidebar.json + index.md

        # Verify output files exist
        module_md = output_dir / "sample_physics.md"
        sidebar_json = output_dir / "_sidebar.json"
        index_md = output_dir / "index.md"
        assert module_md.exists()
        assert sidebar_json.exists()
        assert index_md.exists()

        # Verify module Markdown content
        content = module_md.read_text()
        assert "title: sample_physics" in content
        assert "A sample physics module" in content

        # Variables section
        assert "## Variables" in content or "PI" in content

        # Derived Types section
        assert "config_type" in content

        # Subroutines section
        assert "init" in content

        # Functions section
        assert "compute_dt" in content

        # Verify sidebar JSON
        sidebar = json.loads(sidebar_json.read_text())
        assert isinstance(sidebar, list)
        # At least one group with items
        all_items = [item for group in sidebar for item in group.get("items", [])]
        module_names = [item["text"] for item in all_items]
        assert "sample_physics" in module_names

        # Verify index
        index_content = index_md.read_text()
        assert "API Reference" in index_content
        assert "sample_physics" in index_content
