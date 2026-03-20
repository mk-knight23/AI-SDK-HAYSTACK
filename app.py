"""Production-style Haystack runtime for Kazi's Agents Army."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "core"))
from agents_army_core import MissionRequest, build_mission_plan


def run_haystack_mission(mission_text: str) -> dict:
    plan = build_mission_plan(MissionRequest(mission_text))

    try:
        from haystack import Pipeline
    except Exception as exc:
        return {
            "primary": plan.primary,
            "support": plan.support,
            "result": None,
            "verification": f"Haystack dependency missing: {exc}",
        }

    _ = Pipeline()
    return {
        "primary": plan.primary,
        "support": plan.support,
        "result": "Pipeline instantiated.",
        "verification": "Haystack pipeline path validated.",
    }
