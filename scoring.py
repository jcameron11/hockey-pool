from __future__ import annotations
from typing import Dict, List
import pandas as pd
from nhl_api import SkaterStat

def normalize(s: str) -> str:
    return " ".join(str(s).strip().lower().split())

def build_rank_lookup(skater_stats: List[SkaterStat]) -> Dict[str, int]:
    if not skater_stats:
        return {}
    df = pd.DataFrame([{
        "name": s.name,
        "points": s.points,
        "goals": s.goals,
        "assists": s.assists
    } for s in skater_stats])

    df["name_key"] = df["name"].map(normalize)
    df = df.sort_values(["points","goals","assists","name"], ascending=[False, False, False, True]).reset_index(drop=True)
    df["rank"] = df[["points","goals","assists"]].apply(tuple, axis=1).rank(method="dense", ascending=False).astype(int)

    out={}
    for _, r in df.iterrows():
        k = r["name_key"]
        out[k] = int(r["rank"])
    return out

def build_leaderboard(picks: pd.DataFrame, skater_stats: List[SkaterStat], team_place: Dict[str,int]) -> pd.DataFrame:
    ranks = build_rank_lookup(skater_stats)
    team_place_norm = {normalize(k): int(v) for k,v in (team_place or {}).items()}

    def r(name: str) -> int:
        if not name: return 0
        return int(ranks.get(normalize(name), 0))

    rows=[]
    for _, p in picks.iterrows():
        team = p.get("Team","")
        place = int(team_place_norm.get(normalize(team), 0))
        team_pts = place*5

        f1 = r(p.get("Forward1",""))
        f2 = r(p.get("Forward2",""))
        d  = r(p.get("Defenceman",""))

        total = team_pts + f1 + f2 + d

        rows.append({
            "Entrant": p.get("Entrant",""),
            "Team": team,
            "TeamPlace": place,
            "TeamPts": team_pts,
            "Forward1": p.get("Forward1",""),
            "F1_Rank": f1,
            "Forward2": p.get("Forward2",""),
            "F2_Rank": f2,
            "Defenceman": p.get("Defenceman",""),
            "D_Rank": d,
            "Total": total,
        })

    return pd.DataFrame(rows).sort_values(["Total","Entrant"], ascending=[True, True]).reset_index(drop=True)
