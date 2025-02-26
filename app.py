import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}  # Ensure correct API authentication

# App Title and Description
st.set_page_config(page_title="PropEdge NBA", layout="wide")  # Set wide layout
st.title("🏀 PropEdge NBA")
st.markdown("View today's NBA games and players in each matchup.")

# Dark Mode Toggle
dark_mode = st.sidebar.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body {
            background-color: #121212;
            color: white;
        }
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
                games = []
                for game in data["data"]:
                    # Extract proper game time if available
                    game_time = game.get("datetime", "Unknown Time")
                    if game_time != "Unknown Time":
                        game_time = datetime.strptime(game_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%B %d, %Y - %I:%M %p ET")

                    games.append({
                        "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                        "home_team": game['home_team']['id'],
                        "away_team": game['visitor_team']['id'],
                        "home_team_name": game['home_team']['full_name'],
                        "away_team_name": game['visitor_team']['full_name'],
                        "game_time": game_time
                    })
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
                "name": f"{player['first_name']} {player['last_name']}",
                "position": player.get("position", "N/A"),
                "team": player.get("team", {}).get("full_name", "Unknown"),
                "image": f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player['id']}.png"  # More reliable NBA headshots
            } for player in data.get("data", [])]
        return []
    except:
        return []

# Sidebar: Display Games
st.sidebar.title("📅 Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# Main Content
if selected_game_data:
    st.subheader(f"Players for {selected_game}")
    st.write(f"🕒 Game Time: **{selected_game_data['game_time']}**")  # Fix game time display
    
    # Fetch active players
    home_team_players = fetch_active_players(selected_game_data["home_team"])
    away_team_players = fetch_active_players(selected_game_data["away_team"])
    all_players = home_team_players + away_team_players
    
    if all_players:
        st.write("### Players in this game:")
        
        # Search Bar for Players
        search_query = st.text_input("🔍 Search for a player...")
        
        filtered_players = [p for p in all_players if search_query.lower() in p["name"].lower()] if search_query else all_players
        
        # Display as Table
        player_table = [{
            "Player": p["name"],
            "Position": p["position"],
            "Team": p["team"],
            "Image": f"![img]({p['image']})"
        } for p in filtered_players]
        
        st.table(player_table)
    else:
        st.write("❌ No active players found for this game.")
else:
    st.write("⚠️ No games available today.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
