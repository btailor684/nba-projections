import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}  # Ensure correct API authentication

# App Title and Description
st.title("PropEdge NBA")
st.markdown("View today's NBA games and players in each matchup.")

# --- Fetch Daily NBA Games ---
def fetch_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.balldontlie.io/v1/games?start_date={today}&end_date={today}"
    st.write(f"🔍 Debug: Games API URL - {url}")  # Debugging URL
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        st.write(f"🔍 Debug: API Response Status - {response.status_code}")  # Debugging Status Code
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                games = [
                    {
                        "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                        "home_team_id": game['home_team']['id'],
                        "away_team_id": game['visitor_team']['id']
                    }
                    for game in data["data"]
                ]
                return games if games else []
        return []
    except Exception as e:
        st.write(f"⚠️ Error fetching games: {e}")
        return []

# --- Fetch Active Players in a Game ---
def fetch_active_players(team_id):
    url = f"https://api.balldontlie.io/v1/players/active?team_ids[]={team_id}&per_page=100"
    st.write(f"🔍 Debug: Players API URL - {url}")  # Debugging URL
    try:
        response = requests.get(url, headers=HEADERS)
        st.write(f"🔍 Debug: API Response Status - {response.status_code}")  # Debugging Status Code
        if response.status_code == 200:
            data = response.json()
            st.write(f"🔍 Debug: API Response Data - {data}")  # Debugging Full Response
            players = [f"{player['first_name']} {player['last_name']}" for player in data.get("data", [])]
            return players
        else:
            return []
    except Exception as e:
        st.write(f"⚠️ Error fetching players: {e}")
        return []

# --- Sidebar: Display Games ---
st.sidebar.title("Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# --- Main Content ---
if selected_game_data:
    st.subheader(f"Players for {selected_game}")
    
    # Fetch active players
    home_team_players = fetch_active_players(selected_game_data["home_team_id"])
    away_team_players = fetch_active_players(selected_game_data["away_team_id"])
    all_players = home_team_players + away_team_players
    
    if all_players:
        st.write("### Players in this game:")
        st.table({"Players": all_players})
    else:
        st.write("⚠️ No active players found for this game.")
else:
    st.write("⚠️ No games available today.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
