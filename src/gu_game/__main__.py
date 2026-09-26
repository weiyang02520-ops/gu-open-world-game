"""Headless smoke and integrated V0.1 entry point."""

from __future__ import annotations

import argparse
import json

from .core.state import WorldState
from .m1.scenario import run_and_summarize
from .m2.scenario import run_m2_smoke
from .m3.scenario import run_m3_smoke
from .m4.scenario import run_m4_smoke
from .m5.scenario import run_m5_smoke
from .m6.scenario import run_m6_smoke
from .m7.scenario import run_m7_smoke
from .m8.models import StrategyProfile
from .m8.scenario import run_v01_comparison, run_v01_smoke
from .playable import run_playable
from .save_load import load_game, save_game


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic GU world scenarios")
    parser.add_argument(
        "--scenario",
        choices=(
            "core",
            "day1-2",
            "m2",
            "m3",
            "m4",
            "m5",
            "m6",
            "m7",
            "v0.1",
            "v0.1-compare",
            "play",
            "ui",
        ),
        default="core",
    )
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--interactive", action="store_true", help="use terminal input for the playable scenario")
    parser.add_argument("--strategy", choices=tuple(item.value for item in StrategyProfile), default=StrategyProfile.COOPERATIVE.value)
    args = parser.parse_args()

    if args.scenario == "play":
        print(json.dumps(
            run_playable(args.seed, interactive=args.interactive),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ))
        return
    if args.scenario == "ui":
        from ui.app import run_server

        run_server()
        return
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
    if args.scenario == "m5":
        print(json.dumps(run_m5_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "m6":
        print(json.dumps(run_m6_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "m7":
        print(json.dumps(run_m7_smoke(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "v0.1":
        print(json.dumps(run_v01_smoke(args.seed, args.strategy), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.scenario == "v0.1-compare":
        print(json.dumps(run_v01_comparison(args.seed), ensure_ascii=False, indent=2, sort_keys=True))
        return

    state = WorldState.new(seed=args.seed)
    state.clock.advance(args.seconds)
    print(f"seed={state.world_seed} elapsed_seconds={state.clock.elapsed_seconds} day={state.clock.day_number}")


if __name__ == "__main__":
    main()
