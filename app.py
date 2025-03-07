import streamlit as st
import requests
import pandas as pd

# ✅ Correct API Key (DO NOT REMOVE)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# ✅ Fetch Today's NBA Games
def fetch_games():
    url = f"{BASE_URL}/games"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ✅ Fetch Active Players for a Team
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ✅ Fetch Season Averages (FIXED)
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages?season=2024&player_ids={player_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        stats = response.json().get("data", [])
        return stats[0] if stats else None
    return None

# ✅ Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
games = fetch_games()

game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = game_data["date"]

    st.title("🏀 PropEdge NBA")
    st.subheader(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")

    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    
    players = players_home + players_away
    
    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))

        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")

            # ✅ Display Season Averages (WORKING)
            season_avg = fetch_player_season_averages(player_id)
            if season_avg:
                st.markdown(f"## 📊 **Season Averages for {selected_player}**")
                st.markdown(f"**Points Per Game:** <span style='color:red; font-size:20px;'>{season_avg['pts']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Rebounds Per Game:** <span style='color:blue; font-size:20px;'>{season_avg['reb']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Assists Per Game:** <span style='color:orange; font-size:20px;'>{season_avg['ast']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Field Goal %:** <span style='color:green; font-size:20px;'>{season_avg['fg_pct']*100:.1f}%</span>", unsafe_allow_html=True)
                st.markdown(f"**Minutes Per Game:** <span style='font-weight:bold; font-size:20px;'>{season_avg['min']}</span>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No season averages available for this player.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
