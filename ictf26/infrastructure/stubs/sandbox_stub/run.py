import os
import runpy
import sys


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {name}")
        return default
    return v


def main() -> None:
    # Simulate the organizer-provided sandbox image behavior:
    # run a Python file provided by the challenge/author (mounted into the container).
    #
    # - If a path is passed as argv[1], run that.
    # - Else run $AGENT_FILE if set.
    # - Else default to /workspace/solve.py.
    script_path = sys.argv[1] if len(sys.argv) > 1 else _env("AGENT_FILE", "/workspace/solve.py")

    if not os.path.exists(script_path):
        raise FileNotFoundError(
            f"Script not found: {script_path}. "
            "Mount your solver into the container and/or set AGENT_FILE."
        )

    sys.path.insert(0, os.path.dirname(os.path.abspath(script_path)))
    runpy.run_path(script_path, run_name="__main__")


if __name__ == "__main__":
    main()

