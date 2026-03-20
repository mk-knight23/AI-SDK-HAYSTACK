import argparse

try:
    from .app import run_haystack_mission
except ImportError:
    from app import run_haystack_mission


def demo(mission: str) -> None:
    out = run_haystack_mission(mission)
    print("[Haystack] primary:", out.get("primary"))
    print("[Haystack] support:", out.get("support"))
    print("[Haystack] result:", out.get("result"))
    print("[Haystack] verification:", out.get("verification"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", default="create retrieval pipeline for internal docs")
    args = parser.parse_args()
    demo(args.mission)
