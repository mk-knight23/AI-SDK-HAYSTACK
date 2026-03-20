from fastapi import FastAPI
from pydantic import BaseModel

from app import run_haystack_mission

app = FastAPI(title="Kazi Agents Army - Haystack")


class MissionIn(BaseModel):
    mission: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run")
def run(inp: MissionIn) -> dict:
    return run_haystack_mission(inp.mission)
