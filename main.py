"""Repository-level launcher for the headless GU game scenarios.

The package entry point remains ``gu_game.__main__`` so installed users can
run ``python -m gu_game``.  Keeping this tiny forwarding script makes a fresh
checkout equally easy to start with ``python main.py`` without introducing a
second game authority.  The local ``src`` directory is added only when the
package has not been installed yet, which keeps the command useful in a fresh
clone and in CI.
"""

from pathlib import Path
import sys


_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from gu_game.__main__ import main


if __name__ == "__main__":
    # A bare checkout launch starts the non-interactive 30-day playable demo;
    # pass explicit arguments for the core and milestone smoke scenarios.
    if len(sys.argv) == 1:
        sys.argv.extend(("--scenario", "play"))
    main()
