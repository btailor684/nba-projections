import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ✅ API Key (Ensuring this is always set)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}  # Ensure API key is used properly
BASE_URL = "https://api.balldontlie.io/v1"

### 🔹 FUNCTION: Fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

### 🔹 FUNCTION: Fetch active players for a selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

### 🔹 FUNCTION: Fetch season averages for a player (WITH DEBUGGING)
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages?season=2024&player_ids={player_id}"
    response = requests.get(url, headers=HEADERS)

    # DEBUG: Log full API response
    st.write(f"🔍 Debug: Fetching Season Averages from API: {url}")
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        st.write(f"✅ API Response: {data}")  # Log raw response

        if data:
            return {
                "Points": data[0].get("pts", "N/A"),
                "Rebounds": data[0].get("reb", "N/A"),
                "Assists": data[0].get("ast", "N/A"),
                "Field Goal %": data[0].get("fg_pct", "N/A"),
                "Minutes": data[0].get("min", "N/A"),
            }
        else:
            st.error("⚠️ No season averages data returned by API.")
    else:
        st.error(f"❌ API Error: {response.status_code} - {response.text}")  # Log API error message

    return None  # Return None if no data is found

# 🎨 Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games and players.")

# Fetch Games
games = fetch_games()

game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    
    st.title("🏀 PropEdge NBA")
    st.write("View today's NBA games and players.")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")
    
    # Fetch Active Players
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    players = players_home + players_away

    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")
            
            # Fetch Season Averages (DEBUGGING ENABLED)
            season_avg = fetch_player_season_averages(player_id)
            if season_avg:
                st.subheader(f"📊 Season Averages for {selected_player}")
                df_season_avg = pd.DataFrame([season_avg])
                st.table(df_season_avg)
            else:
                st.warning("⚠️ No season averages available for this player.")

    else:
        st.warning("⚠️ No active players found for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
