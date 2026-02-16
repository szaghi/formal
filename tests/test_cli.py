"""Tests for CLI argument parsing and command dispatch."""

import pytest
from formal.cli import main


class TestCLI:
    def test_version(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "formal" in captured.out
        assert "0.1.0" in captured.out

    def test_no_args_prints_help(self, capsys):
        """No subcommand should print help and exit 0."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 0

    def test_init_help(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["init", "--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "project_root" in captured.out

    def test_generate_help(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["generate", "--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "--project" in captured.out

    def test_init_creates_files(self, tmp_path):
        result = main(["init", str(tmp_path)])
        assert result == 0
        assert (tmp_path / "doc" / "formal.md").exists()
        assert (tmp_path / "docs" / "package.json").exists()
        assert (tmp_path / "docs" / ".vitepress" / "config.mts").exists()
        assert (tmp_path / "docs" / "index.md").exists()

    def test_init_nonexistent_dir(self, tmp_path, capsys):
        result = main(["init", str(tmp_path / "nonexistent")])
        assert result == 1
        captured = capsys.readouterr()
        assert "not a directory" in captured.err

    def test_init_with_options(self, tmp_path):
        result = main([
            "init", str(tmp_path),
            "--name", "CustomProject",
            "--src-dir", "../src/lib", "../src/app",
            "--docs-dir", "documentation",
            "--author", "Test Author",
            "--no-math",
        ])
        assert result == 0
        ford_file = tmp_path / "doc" / "formal.md"
        content = ford_file.read_text()
        assert "project: CustomProject" in content
        assert "author: Test Author" in content
        assert (tmp_path / "documentation" / "package.json").exists()

    def test_generate_nonexistent_project(self, tmp_path, monkeypatch):
        """generate with nonexistent project file should return 1."""
        monkeypatch.chdir(tmp_path)
        result = main(["generate", "--project", str(tmp_path / "nope.md")])
        assert result == 1
