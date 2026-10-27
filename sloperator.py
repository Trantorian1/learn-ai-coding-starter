import argparse
import sys
from pathlib import Path

from sloperator.runner import run_program, validate


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sloperator.py",
        description="Run a SlopLang program.",
    )
    parser.add_argument("filename", help="path to the .slop program to run")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check the file's syntax without executing it",
    )
    args = parser.parse_args(argv[1:])

    path = Path(args.filename)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"could not read '{path}': {error.strerror}", file=sys.stderr)
        return 2

    if args.check:
        error = validate(source)
        if error is not None:
            print(error, file=sys.stderr)
            return 1
        print(f"validated '{path}' successfully")
        return 0

    error = run_program(source, sys.stdout)
    if error is not None:
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
