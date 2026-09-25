"""Small headless smoke entry point for the M0 core."""

from __future__ import annotations

import argparse
import json

from .core.state import WorldState
from .m1.scenario import run_and_summarize
from .m2.scenario import run_m2_smoke
from .m3.scenario import run_m3_smoke
from .m4.scenario import run_m4_smoke


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal GU simulation smoke step")
    parser.add_argument(
        "--scenario",
        choices=("core", "day1-2", "m2", "m3", "m4"),
        default="core",
        help="run the M0 core, M1 Day 1~2, M2 combat, M3 information or M4 faction smoke",
    )
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--seconds", type=int, default=60)
    args = parser.parse_args()

    if args.scenario == "day1-2":
        result = run_and_summarize(args.seed)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "m2":
        print(json.dumps(run_m2_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "m3":
        print(json.dumps(run_m3_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "m4":
        print(json.dumps(run_m4_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return

    state = WorldState.new(seed=args.seed)
    state.clock.advance(args.seconds)
    print(
        f"seed={state.world_seed} elapsed_seconds={state.clock.elapsed_seconds} "
        f"day={state.clock.day_number}"
    )


if __name__ == "__main__":  # pragma: no cover
    main()
