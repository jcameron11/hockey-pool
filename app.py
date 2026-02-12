from __future__ import annotations
import streamlit as st
import pandas as pd

from picks import load_picks_csv
from nhl_api import fetch_skater_stats, fetch_medal_placements
from scoring import build_leaderboard

DEFAULT_SKATER_API_URL = 'https://records.nhl.com/site/api/international-skater-tournament-record?cayenneExp=gameType=9%20and%20season=20252026&sort=[{%22property%22:%20%22points%22,%20%22direction%22:%20%22DESC%22},%20{%22property%22:%22goals%22,%22direction%22:%22DESC%22},%20{%22property%22:%22gamesPlayed%22,%20%22direction%22:%20%22ASC%22},%20{%22property%22:%22lastName%22,%22direction%22:%22ASC%22}]'
DEFAULT_WINNER_API_URL = 'https://records.nhl.com/site/api/international-tournament-winner?&sort=[{%22property%22:%20%22season%22,%20%22direction%22:%20%22DESC%22}]&cayenneExp=gameType=9'
DEFAULT_SEASON = "20252026"

st.set_page_config(page_title="Olympics Hockey Pool Tracker", layout="wide")
st.title("🏒 Olympics Hockey Pool Tracker (Zero defaults)")

with st.sidebar:
    picks_path = st.text_input("Picks CSV filename", value="2026 Olympics Picks - Sheet1.csv")
    picks_upload = st.file_uploader("Or upload your picks CSV", type=["csv"])
    season = st.text_input("Season", value=DEFAULT_SEASON)
    skater_api_url = st.text_input("Skater stats API URL", value=DEFAULT_SKATER_API_URL)
    winner_api_url = st.text_input("Tournament winner API URL", value=DEFAULT_WINNER_API_URL)
    refresh = st.button("🔄 Refresh from NHL")

try:
    picks_df = load_picks_csv(picks_upload) if picks_upload is not None else load_picks_csv(picks_path)
except Exception as err:
    st.error(f"Couldn't load picks CSV: {err}")
    st.stop()

if refresh or "skater_stats" not in st.session_state:
    try:
        st.session_state["skater_stats"] = fetch_skater_stats(skater_api_url)
    except Exception:
        st.session_state["skater_stats"] = []
    try:
        st.session_state["auto_place"] = fetch_medal_placements(winner_api_url, season)
    except Exception:
        st.session_state["auto_place"] = {}

skater_stats = st.session_state.get("skater_stats", [])
auto_place = st.session_state.get("auto_place", {})

prefill = [{"Team": k, "Placement": v} for k, v in sorted(auto_place.items(), key=lambda kv: kv[1])] or [{"Team":"", "Placement":""}]
tp_df = st.data_editor(pd.DataFrame(prefill), num_rows="dynamic", use_container_width=True, hide_index=True)

team_place = {}
for _, r in tp_df.iterrows():
    team = str(r.get("Team","")).strip()
    placement = str(r.get("Placement","")).strip()
    if team and placement.isdigit():
        team_place[team] = int(placement)

leader = build_leaderboard(picks_df, skater_stats, team_place)
st.dataframe(leader, use_container_width=True, hide_index=True)
