import json
import re
import subprocess
import tempfile
from pathlib import Path

AGENTS_DIR = Path("data/agents")
CACHE_PATH = AGENTS_DIR / "agents.json"
# Порядок файлов фиксирует диапазоны agent_id (1-44).
FILE_ORDER = ["trajectory", "materials", "feedback", "gamification", "collaboration"]

_IMPORT_RE = re.compile(r"^\s*import\b.*$", re.MULTILINE)
_EXPORT_RE = re.compile(r"export\s+const\s+\w+\s*:\s*AgentSpec\[\]\s*=")


def _ts_to_objects(ts_path: Path) -> list[dict]:
    """Strip TS-only syntax and eval the array literal via node into JSON."""
    src = ts_path.read_text(encoding="utf-8")
    src = _IMPORT_RE.sub("", src)
    src = _EXPORT_RE.sub("module.exports =", src, count=1)
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8") as f:
        f.write(src)
        tmp = f.name
    try:
        completed = subprocess.run(
            ["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(tmp)})))"],
            capture_output=True,
            text=True,
            check=True,
        )
    finally:
        Path(tmp).unlink(missing_ok=True)
    return json.loads(completed.stdout)


def build_agents_json() -> list[dict]:
    agents: list[dict] = []
    agent_id = 1
    for stem in FILE_ORDER:
        for obj in _ts_to_objects(AGENTS_DIR / f"{stem}.ts"):
            obj["agent_id"] = agent_id
            agents.append(obj)
            agent_id += 1
    CACHE_PATH.write_text(json.dumps(agents, ensure_ascii=False, indent=2), encoding="utf-8")
    return agents


def load_agents(force_rebuild: bool = False) -> list[dict]:
    if force_rebuild or not CACHE_PATH.exists():
        return build_agents_json()
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
