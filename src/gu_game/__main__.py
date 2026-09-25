"""Small headless smoke entry point for the M0 core."""

from __future__ import annotations

import argparse

from .core.state import WorldState


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal GU simulation smoke step")
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--seconds", type=int, default=60)
    args = parser.parse_args()

    state = WorldState.new(seed=args.seed)
    state.clock.advance(args.seconds)
    print(
        f"seed={state.world_seed} elapsed_seconds={state.clock.elapsed_seconds} "
        f"day={state.clock.day_number}"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
