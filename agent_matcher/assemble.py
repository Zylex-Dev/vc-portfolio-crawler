import pandas as pd

THRESHOLD = 7


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

        rows.append({
            "id": int(r["id"]),
            "name": r.get("name"),
            "fund": r.get("fund"),
            "sectors": r.get("sectors"),
            "pmo_score": r.get("pmo_score"),
            "assigned_agent": assigned,
            "agent_sredstvo": sredstvo,
            "agent_status": status,
            "relevance": rel,
            "rationale": res.get("rationale", ""),
        })
    return pd.DataFrame(rows)


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
