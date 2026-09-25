"""M2 combat, injury and hostile decision loop."""

from .balance import GAME_EXTENSION_COMBAT_BALANCE
from .engine import CombatEngine, CombatValidationError
from .models import (
    BodyPart,
    CombatActionType,
    CombatDecision,
    CombatEncounter,
    CombatGuProfile,
    CombatStatus,
    InjurySeverity,
    PerceivedCombatSnapshot,
)

__all__ = [
    "BodyPart",
    "CombatActionType",
    "CombatDecision",
    "CombatEngine",
    "CombatEncounter",
    "CombatGuProfile",
    "CombatStatus",
    "CombatValidationError",
    "GAME_EXTENSION_COMBAT_BALANCE",
    "InjurySeverity",
    "PerceivedCombatSnapshot",
]
