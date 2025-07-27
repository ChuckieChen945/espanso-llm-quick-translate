"""_summary_."""

import sys

from core.ask_ai import ask_ai, load_and_validate_env
from core.background_worker import spawn_background_task_cli


def main() -> None:
    """
    Enter the script.

    Parses arguments, validates input, calls ask_ai, and prints the result.
    """
    if len(sys.argv) != 2:
        print('❌ Usage error: python main.py "<text>"')  # noqa: T201
        return
    original = sys.argv[1]
    if not original.strip():
        print("❌ Error: No prompt text provided!")  # noqa: T201
        return
    translated = ask_ai(original)
    print(translated, flush=True)  # noqa: T201

    return


if __name__ == "__main__":
    main()
