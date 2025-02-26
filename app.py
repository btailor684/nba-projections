import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}

# App Title and Description
st.set_page_config(page_title="PropEdge NBA", layout="wide")  
st.title("🏀 PropEdge NBA")
st.markdown("View today's NBA games, players, and stats.")

# Dark Mode Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #121212; color: white; }
        </style>
        """, unsafe_allow_html=True)

# Fetch Daily NBA Games
def fetch_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.balldontlie.io/v1/games?start_date={today}&end_date={today}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                games = [
                    {
                        "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                        "home_team": game['home_team']['id'],
                        "away_team": game['visitor_team']['id'],
                        "game_time": game.get('status', 'Time Unknown')
                    }
                    for game in data["data"]
                ]
                return games if games else []
        return []
    except Exception as e:
        return []

# Fetch Active Players in Game
def fetch_active_players(team_id):
    url = f"https://api.balldontlie.io/v1/players/active?team_ids[]={team_id}&per_page=100"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return [{
                "id": player["id"],
                "name": f"{player['first_name']} {player['last_name']}",
                "position": player.get("position", "N/A"),
                "team": player.get("team", {}).get("full_name", "Unknown"),
            } for player in data.get("data", [])]
        return []
    except:
        return []

# Fetch Player Stats
def fetch_player_stats(player_id):
    url = f"https://api.balldontlie.io/v1/season_averages?season=2024&player_ids[]={player_id}"
    
    # Debug: Print URL to ensure the correct player_id is passed
    st.write(f"🔍 Debug: Player Stats API Request - {url}")

    try:
        response = requests.get(url, headers=HEADERS)
        
        # Debug: Print full API response
        st.write(f"🔍 Debug: API Response - {response.json()}")

        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                stats = data["data"][0]
                return {
                    "PTS": stats.get("pts", 0),
                    "AST": stats.get("ast", 0),
                    "REB": stats.get("reb", 0),
                    "FG%": round(stats.get("fg_pct", 0) * 100, 1) if stats.get("fg_pct") else 0
                }
        return None
    except:
        return None

# Sidebar: Display Games
st.sidebar.title("📅 Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# Main Content
if selected_game_data:
    st.subheader(f"Players for {selected_game}")
    st.write(f"🕒 Game Time: **{selected_game_data['game_time']}**")

    # Fetch active players
    home_team_players = fetch_active_players(selected_game_data["home_team"])
    away_team_players = fetch_active_players(selected_game_data["away_team"])
    all_players = home_team_players + away_team_players

    if all_players:
        st.write("### Players in this game:")

        # Player Selection Dropdown
        player_names = [p["name"] for p in all_players]
        selected_player_name = st.selectbox("Select a Player", player_names)

        # Find the selected player ID
        selected_player = next((p for p in all_players if p["name"] == selected_player_name), None)

        if selected_player:
            st.write(f"🔎 Fetching stats for: **{selected_player_name} (ID: {selected_player['id']})**")

            # Fetch and Display Player Stats
            player_stats = fetch_player_stats(selected_player["id"])

            if player_stats:
                st.write(f"### Stats for {selected_player_name}")
                st.metric("Points Per Game", player_stats["PTS"])
                st.metric("Assists Per Game", player_stats["AST"])
                st.metric("Rebounds Per Game", player_stats["REB"])
                st.metric("Field Goal %", f"{player_stats['FG%']}%")
            else:
                st.warning("⚠️ No stats available for this player.")
    else:
        st.write("❌ No active players found for this game.")
else:
    st.write("⚠️ No games available today.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
