"""Small headless smoke entry point for the M0 core."""

from __future__ import annotations

import argparse
import json

from .core.state import WorldState
from .m1.scenario import run_and_summarize


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal GU simulation smoke step")
    parser.add_argument(
        "--scenario",
        choices=("core", "day1-2"),
        default="core",
        help="run the M0 core smoke or the M1 Day 1~2 sandbox",
    )
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--seconds", type=int, default=60)
    args = parser.parse_args()

    if args.scenario == "day1-2":
        result = run_and_summarize(args.seed)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return

    state = WorldState.new(seed=args.seed)
    state.clock.advance(args.seconds)
    print(
        f"seed={state.world_seed} elapsed_seconds={state.clock.elapsed_seconds} "
        f"day={state.clock.day_number}"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
