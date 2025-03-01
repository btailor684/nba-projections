import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Key
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# Function to fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Function to fetch active players for a selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players/active?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games and players.")

games = fetch_games()
game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    
    st.title("🏀 PropEdge NBA")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")
    
    # Fetch players from both teams
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    players = players_home + players_away
    
    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player for player in players}
        selected_player_name = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player_name:
            player_info = player_dict[selected_player_name]
            st.write(f"📊 **Player Details for: {selected_player_name}**")
            st.write(f"- **Position:** {player_info.get('position', 'N/A')}")
            st.write(f"- **Height:** {player_info.get('height', 'N/A')}")
            st.write(f"- **Weight:** {player_info.get('weight', 'N/A')}")
            st.write(f"- **College:** {player_info.get('college', 'N/A')}")
            st.write(f"- **Country:** {player_info.get('country', 'N/A')}")
    else:
        st.warning("⚠️ No active players found for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
