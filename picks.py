from __future__ import annotations
import pandas as pd

def load_picks_csv(path_or_buffer) -> pd.DataFrame:
    raw = pd.read_csv(path_or_buffer)
    header = [str(x).strip() if pd.notna(x) else "" for x in raw.iloc[0].tolist()]
    data = raw.iloc[1:].copy()

    canon = {
        "picks": "Entrant",
        "": "Entrant",
        "name": "Entrant",
        "team": "Team",
        "forward 1": "Forward1",
        "forward 2": "Forward2",
        "defenceman": "Defenceman",
        "defenseman": "Defenceman",
    }

    cols = []
    for i, h in enumerate(header):
        cols.append(canon.get(h.strip().lower(), raw.columns[i]))
    data.columns = cols

    for c in ["Entrant","Team","Forward1","Forward2","Defenceman"]:
        if c not in data.columns:
            data[c] = ""

    for c in ["Entrant","Team","Forward1","Forward2","Defenceman"]:
        data[c] = data[c].astype(str).str.strip().replace({"nan":"", "None":""})

    return data.reset_index(drop=True)[["Entrant","Team","Forward1","Forward2","Defenceman"]]
