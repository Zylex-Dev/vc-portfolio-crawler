#!/usr/bin/env python3
"""Convert the research outputs into the landing's data contract.

Reads from ../data (repo-level) and writes src/data/report.json:

    {
      meta:     { totalStartups, totalAgents, matched, unmatched, totalFunds },
      agents:   [ { id, name, category, sredstvo, status, role, userStory,
                    resourceLink, comment, functionalRequirements[],
                    expectedBehavior, inputs, outputs,
                    cjmClassroom, cjmPlatform } ],
      startups: [ { id, fund, name, sectors[], website, description, stage,
                    foundedYear, pmoScore, pmoSub{...}, relevance, rationale,
                    assignedAgent } ]
    }

The agent objects carry the full detail set so the landing's per-agent
modal can render everything without a second data source.

Metrics stay on their native 0-10 scale; the UI scales bars at render time.
Run: python3 scripts/build_data.py
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
OUT = os.path.normpath(os.path.join(HERE, "..", "src", "data", "report.json"))

UNMATCHED = "unmatched"

# Human labels for the funds (slugs in the CSV).
FUND_LABELS = {
    "y-combinator": "Y Combinator",
    "new-schools": "NewSchools",
    "reach-capital": "Reach Capital",
    "learn-capital": "Learn Capital",
    "owl-ventures": "Owl Ventures",
    "gsv-ventures": "GSV Ventures",
    "edu-capital": "Edu Capital",
    "a16z": "a16z",
    "a16z-speedrun": "a16z Speedrun",
    "brighteye": "Brighteye",
    "sequoia": "Sequoia",
}


def num(v, default=None):
    v = (v or "").strip()
    if v == "":
        return default
    try:
        f = float(v)
        return int(f) if f.is_integer() else round(f, 1)
    except ValueError:
        return default


def year(v):
    n = num(v)
    return int(n) if n is not None else None


def main():
    agents_raw = json.load(open(os.path.join(DATA_DIR, "agents.json"), encoding="utf-8"))
    rows = list(csv.DictReader(open(os.path.join(DATA_DIR, "startup_agent_assignment.csv"), encoding="utf-8")))
    # Full crawl before EdTech filtering — the top of the research funnel.
    total_collected = sum(1 for _ in csv.DictReader(open(os.path.join(DATA_DIR, "all_companies.csv"), encoding="utf-8")))

    # Functional grouping of the 232 unmatched ("new ideas"), keyed by startup id.
    # Splits them into 7 niches (G1–G7) and carries a per-startup AI rationale.
    idea_groups = {}
    for g in csv.DictReader(open(os.path.join(DATA_DIR, "unmatched_groups.csv"), encoding="utf-8")):
        idea_groups[g["id"]] = {
            "functionalGroup": (g["functional_group"] or "").strip(),
            "groupRationale": (g["group_rationale"] or "").strip(),
        }

    agents = []
    for a in agents_raw:
        agents.append({
            "id": a["agent_id"],
            "name": a["name"],
            "category": a["sredstvo"],          # 5 средство-groups, shown as domain
            "sredstvo": a["sredstvo"],
            "status": a["developmentStatus"],   # "В разработке" | "Протестировать"
            "role": a.get("role", ""),
            "userStory": a.get("userStory", ""),
            "resourceLink": a.get("resourceLink", ""),
            "comment": (a.get("comment") or "").strip(),
            "functionalRequirements": [r for r in a.get("functionalRequirements", []) if r],
            "expectedBehavior": (a.get("expectedBehavior") or "").strip(),
            "inputs": (a.get("inputs") or "").strip(),
            "outputs": (a.get("outputs") or "").strip(),
            "cjmClassroom": (a.get("cjmClassroom") or "").strip(),
            "cjmPlatform": (a.get("cjmPlatform") or "").strip(),
        })

    startups = []
    funds = set()
    matched = 0
    for r in rows:
        assigned = (r["assigned_agent"] or "").strip()
        is_matched = assigned and assigned != UNMATCHED
        if is_matched:
            matched += 1
        funds.add(r["fund"])
        sectors = [s.strip() for s in (r["sectors"] or "").split(";") if s.strip()]
        idea = idea_groups.get(r["id"], {})
        startups.append({
            "id": int(r["id"]),
            "fund": FUND_LABELS.get(r["fund"], r["fund"]),
            "name": r["name"].strip(),
            "sectors": sectors,
            "website": (r["website"] or "").strip(),
            "description": (r["description"] or "").strip(),
            "stage": (r["stage"] or "").strip(),
            "foundedYear": year(r["founded_year"]),
            "investedYear": year(r["invested_year"]),
            "pmoScore": num(r["pmo_score"], 0),
            "pmoSub": {
                "traj": num(r["pmo_traj"], 0),
                "mat": num(r["pmo_mat"], 0),
                "collab": num(r["pmo_collab"], 0),
                "game": num(r["pmo_game"], 0),
                "feedback": num(r["pmo_feedback"], 0),
            },
            "relevance": num(r["relevance"], 0),
            "rationale": (r["rationale"] or "").strip(),
            "assignedAgent": assigned if is_matched else UNMATCHED,
            # Niche bucket + AI rationale for unmatched "new ideas" (null for matched).
            "functionalGroup": idea.get("functionalGroup"),
            "groupRationale": idea.get("groupRationale", ""),
        })

    report = {
        "meta": {
            "totalCollected": total_collected,
            "totalStartups": len(startups),
            "totalAgents": len(agents),
            "matched": matched,
            "unmatched": len(startups) - matched,
            "totalFunds": len(funds),
        },
        "agents": agents,
        "startups": startups,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, separators=(",", ":"))

    m = report["meta"]
    print(f"Wrote {OUT}")
    print(f"  collected={m['totalCollected']} edtech={m['totalStartups']} matched={m['matched']} "
          f"unmatched={m['unmatched']} agents={m['totalAgents']} funds={m['totalFunds']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
