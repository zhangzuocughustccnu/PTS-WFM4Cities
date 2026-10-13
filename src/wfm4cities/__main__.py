"""Allow ``python -m wfm4cities`` to behave like the command-line program."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
