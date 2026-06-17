import pandas as pd

THRESHOLD = 7


# Колонки из входного датасета
_PASSTHROUGH = [
    "fund", "name", "sectors", "website", "description",
    "stage", "stage_year", "founded_year", "invested_year",
    "pmo_score", "pmo_traj", "pmo_mat", "pmo_collab", "pmo_game",
    "pmo_feedback", "pmo_notes",
]


def build_assignment_df(
    df: pd.DataFrame,
    results: dict[str, dict],
    agents: list[dict],
    threshold: int = THRESHOLD,
) -> pd.DataFrame:
    by_id = {a["agent_id"]: a for a in agents}
    rows = []
    for _, r in df.iterrows():
        res = results.get(
            str(r["id"]), {"agent_id": -1, "relevance": -1, "rationale": "missing"}
        )
        aid = res["agent_id"]
        rel = res["relevance"]

        if aid == -1:
            assigned, sredstvo, status = "error", "", ""
        elif aid == 0 or aid not in by_id or rel < threshold:
            assigned, sredstvo, status = "unmatched", "", ""
        else:
            agent = by_id[aid]
            assigned = agent["name"]
            sredstvo = agent["sredstvo"]
            status = agent.get("developmentStatus", "")

        row = {col: r.get(col) for col in _PASSTHROUGH}
        row["id"] = int(r["id"])
        row["assigned_agent"] = assigned
        row["agent_sredstvo"] = sredstvo
        row["agent_status"] = status
        row["relevance"] = rel
        row["rationale"] = res.get("rationale", "")
        rows.append(row)

    columns = [
        "id", "fund", "name", "sectors", "website", "description",
        "stage", "stage_year", "founded_year", "invested_year",
        "pmo_score", "pmo_traj", "pmo_mat", "pmo_collab", "pmo_game",
        "pmo_feedback", "pmo_notes",
        "assigned_agent", "agent_sredstvo", "agent_status",
        "relevance", "rationale",
    ]
    return pd.DataFrame(rows, columns=columns)


def _format_startups(sub: pd.DataFrame) -> str:
    sub = sub.sort_values("relevance", ascending=False)
    return "; ".join(
        f"{name} ({int(rel)})" for name, rel in zip(sub["name"], sub["relevance"])
    )


def build_agent_pivot_df(assignment: pd.DataFrame, agents: list[dict]) -> pd.DataFrame:
    rows = []
    for a in agents:
        sub = assignment[assignment["assigned_agent"] == a["name"]]
        rows.append({
            "agent_id": a["agent_id"],
            "agent_name": a["name"],
            "sredstvo": a["sredstvo"],
            "developmentStatus": a.get("developmentStatus", ""),
            "num_startups": len(sub),
            "startups": _format_startups(sub),
        })
    for group in ("unmatched", "error"):
        sub = assignment[assignment["assigned_agent"] == group]
        rows.append({
            "agent_id": "",
            "agent_name": group,
            "sredstvo": "",
            "developmentStatus": "",
            "num_startups": len(sub),
            "startups": _format_startups(sub),
        })
    return pd.DataFrame(rows)
