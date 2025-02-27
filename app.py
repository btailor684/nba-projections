import streamlit as st
import requests
from datetime import datetime

# Set API Key (ALWAYS INCLUDED)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}

# Streamlit UI Enhancements
st.set_page_config(page_title="PropEdge NBA", layout="wide")

# Sidebar with Title and Dark Mode Toggle
with st.sidebar:
    st.title("📅 Today's NBA Games")
    st.write("View today's NBA games, players, and stats.")
    dark_mode = st.toggle("🌙 Dark Mode")

# --- Fetch Daily NBA Games ---
def fetch_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.balldontlie.io/v1/games?start_date={today}&end_date={today}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        games = [
            {
                "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                "home_team_id": game['home_team']['id'],
                "away_team_id": game['visitor_team']['id'],
                "time": game['status']  # Fixes game time display
            }
            for game in data['data']
        ]
        return games
    return []

# --- Fetch Active Players for a Team ---
def fetch_active_players(team_id):
    url = f"https://api.balldontlie.io/v1/players/active?team_ids[]={team_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        players = response.json().get("data", [])
        return players
    return []

# --- Fetch Player Stats ---
def fetch_player_stats(player_id):
    url = f"https://api.balldontlie.io/v1/season_averages?season=2024&player_ids[]={player_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        stats = response.json().get("data", [])
        return stats[0] if stats else None
    return None

# Fetch games for today
games = fetch_nba_games()

# Sidebar - Select a Game
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)

# Find selected game data
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# Main Content
st.markdown("## 🏀 **PropEdge NBA**")
st.write("View today's NBA games, players, and stats.")

if selected_game_data:
    st.markdown(f"### **Players for {selected_game}**")
    st.markdown(f"⏰ **Game Time:** {selected_game_data['time']}")

    # Fetch Active Players for both teams
    home_players = fetch_active_players(selected_game_data["home_team_id"])
    away_players = fetch_active_players(selected_game_data["away_team_id"])
    
    # Merge Home and Away Players
    all_players = home_players + away_players

    if all_players:
        # Create a dropdown to select a player
        player_names = {f"{p['first_name']} {p['last_name']}": p['id'] for p in all_players}
        selected_player_name = st.selectbox("Select a Player", list(player_names.keys()))

        # Fetch and display player stats
        if selected_player_name:
            player_id = player_names[selected_player_name]
            st.markdown(f"🔍 Fetching stats for: **{selected_player_name} (ID: {player_id})**")
            
            player_stats = fetch_player_stats(player_id)
            if player_stats:
                st.table({
                    "Stat": ["Games Played", "Points Per Game", "Assists Per Game", "Rebounds Per Game"],
                    "Value": [
                        player_stats.get("games_played", "N/A"),
                        player_stats.get("pts", "N/A"),
                        player_stats.get("ast", "N/A"),
                        player_stats.get("reb", "N/A"),
                    ]
                })
            else:
                st.warning("⚠️ No stats available for this player.")
    else:
        st.warning("⚠️ No active players found for this game.")
else:
    st.error("No games available today. Try again later.")

# Footer
st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
