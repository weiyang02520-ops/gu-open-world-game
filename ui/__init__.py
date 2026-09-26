"""UI adapters for the deterministic GU game core.

Only :class:`GameController` is part of the Phase 1 public UI contract.  The
package deliberately contains no rendering toolkit dependency.
"""

from .controller import GameController

__all__ = ["GameController"]
