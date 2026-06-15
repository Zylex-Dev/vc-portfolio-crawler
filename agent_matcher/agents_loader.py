import json
from pathlib import Path

# data/agents.json — источник истины по 44 агентам (name, sredstvo, role,
# expectedBehavior, developmentStatus, agent_id 1-44 и др.).
AGENTS_PATH = Path("data/agents.json")


def load_agents() -> list[dict]:
    return json.loads(AGENTS_PATH.read_text(encoding="utf-8"))
