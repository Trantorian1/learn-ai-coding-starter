import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERPRETER = ROOT / "sloperator.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTERPRETER), *args], capture_output=True, encoding="utf-8"
    )


def test_runs_a_file():
    completed = run_cli(str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stdout == "hello, slop\n"
    assert completed.stderr == ""


def test_error_goes_to_stderr_after_earlier_output(tmp_path: Path):
    program = tmp_path / "boom.slop"
    program.write_text("hallucinate(“before”)✨\nhallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == "before\n"
    assert completed.stderr == "SlopLang runtime error at line 2: undefined variable 'missing'\n"
    assert "Traceback" not in completed.stderr


def test_missing_file_and_usage():
    assert run_cli().returncode == 2
    missing = run_cli(str(ROOT / "nope.slop"))
    assert missing.returncode == 2
    assert "could not read" in missing.stderr


def test_missing_file_prints_argparse_usage():
    completed = run_cli()
    assert completed.returncode == 2
    assert "usage: sloperator.py" in completed.stderr
    assert "the following arguments are required: filename" in completed.stderr


def test_check_passes_on_a_valid_file():
    completed = run_cli("--check", str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "validated" in completed.stdout


def test_check_reports_a_syntax_error(tmp_path: Path):
    program = tmp_path / "broken.slop"
    program.write_text("hallucinate(“oops)✨", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "SlopLang lexical error" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_check_does_not_execute_runtime_errors(tmp_path: Path):
    program = tmp_path / "runtime.slop"
    program.write_text("hallucinate(missing)✨", encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 0
    assert completed.stderr == ""
