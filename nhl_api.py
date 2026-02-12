from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
import requests

@dataclass
class SkaterStat:
    name: str
    team: str
    position: str
    points: int
    goals: int
    assists: int

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()

)

def _to_int(x) -> int:
    try:
        return int(x)
    except Exception:
        m = re.search(r"-?\d+", str(x))
        return int(m.group(0)) if m else 0

def _get_json(url: str, timeout_s: int = 30) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://records.nhl.com/",
    }
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.json()

def fetch_skater_stats(api_url: str) -> List[SkaterStat]:
    j = _get_json(api_url)
    rows = j.get("data") or j.get("results") or j.get("items") or []
    out: List[SkaterStat] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        first = _norm(str(row.get("firstName", "")))
        last = _norm(str(row.get("lastName", "")))
        name = _norm((first + " " + last).strip()) or _norm(str(row.get("playerName","")))

        team = _norm(str(row.get("teamAbbrev", ""))) or _norm(str(row.get("team", ""))) or _norm(str(row.get("nation","")))
        pos = _norm(str(row.get("positionCode", ""))) or _norm(str(row.get("position","")))

        pts = _to_int(row.get("points", 0))
        g = _to_int(row.get("goals", 0))
        a = _to_int(row.get("assists", 0))

        if name:
            out.append(SkaterStat(name=name, team=team, position=pos, points=pts, goals=g, assists=a))
    return out

def _pick_first(d: Dict[str, Any], keys: List[str]) -> Optional[str]:
    for k in keys:
        v = d.get(k)
        if v is None:
            continue
        if isinstance(v, dict):
            for kk in ["teamAbbrev","team","country","nation","name","abbrev"]:
                vv = v.get(kk)
                if vv:
                    return _norm(str(vv))
        else:
            s = _norm(str(v))
            if s:
                return s
    return None

def fetch_medal_placements(winner_api_url: str, season: str) -> Dict[str, int]:
    j = _get_json(winner_api_url)
    rows = j.get("data") or j.get("results") or j.get("items") or []
    if not isinstance(rows, list):
        return {}

    target = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        s = str(row.get("season") or row.get("seasonId") or row.get("seasonID") or "").strip()
        if s == season:
            target = row
            break

    if not target:
        return {}

    gold = _pick_first(target, ["gold", "goldTeam", "goldCountry", "champion", "winner", "firstPlace", "team1", "teamFirst", "winnerTeamAbbrev"])
    silver = _pick_first(target, ["silver", "silverTeam", "silverCountry", "runnerUp", "secondPlace", "team2", "teamSecond", "runnerUpTeamAbbrev"])
    bronze = _pick_first(target, ["bronze", "bronzeTeam", "bronzeCountry", "thirdPlace", "team3", "teamThird", "thirdPlaceTeamAbbrev"])

    out: Dict[str,int] = {}
    if gold: out[gold] = 1
    if silver: out[silver] = 2
    if bronze: out[bronze] = 3
    return out
