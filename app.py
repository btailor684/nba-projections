import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}  # Ensure correct API authentication

# App Title and Description
st.title("PropEdge NBA")
st.markdown("Your daily edge for NBA player prop bets. Get projections and recommendations for points, assists, and rebounds.")

# --- Fetch Daily NBA Games ---
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
                        "away_team": game['visitor_team']['id']
                    }
                    for game in data["data"]
                ]
                return games if games else [{"matchup": "No games found today", "home_team": "", "away_team": ""}]
        return [{"matchup": f"API Error (Status: {response.status_code})", "home_team": "", "away_team": ""}]
    except Exception as e:
        return [{"matchup": f"Error: {str(e)}", "home_team": "", "away_team": ""}]

# --- Fetch Active Players in Game ---
def fetch_active_players(team_id):
    url = f"https://api.balldontlie.io/v1/players?team_ids[]={team_id}&per_page=100"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return [f"{player['first_name']} {player['last_name']}" for player in data.get("data", [])]
        return []
    except:
        return []

# --- Fetch Player ID ---
def get_player_id(player_name):
    url = "https://api.balldontlie.io/v1/players"
    try:
        response = requests.get(url, headers=HEADERS, params={"search": player_name, "per_page": 10})
        if response.status_code == 200:
            data = response.json()
            for player in data.get("data", []):
                if f"{player['first_name']} {player['last_name']}".lower() == player_name.lower():
                    return player["id"]
        st.write(f"⚠️ Player ID not found for {player_name}")
        return None
    except Exception as e:
        st.write(f"❌ Error retrieving player ID: {str(e)}")
        return None

# --- Fetch Player Stats ---
def fetch_player_stats(player_id):
    url = "https://api.balldontlie.io/v1/season_averages"
    params = {
        "season": 2024,
        "player_ids": player_id  # Ensure correct format
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                stats = data["data"][0]
                return {
                    "pts": stats.get("pts", 0),
                    "ast": stats.get("ast", 0),
                    "reb": stats.get("reb", 0),
                    "min": float(stats.get("min", "0").split(":")[0])
                }
            else:
                st.write(f"⚠️ No stats available for player ID {player_id}")
        else:
            st.write(f"❌ API Error fetching player stats: {response.status_code}")
        return {"pts": 0, "ast": 0, "reb": 0, "min": 0}
    except Exception as e:
        st.write(f"❌ Error retrieving player stats: {str(e)}")
        return {"pts": 0, "ast": 0, "reb": 0, "min": 0}

# --- Sidebar: Display Games ---
st.sidebar.title("Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# --- Main Content ---
if selected_game_data and "No games" not in selected_game and "Error" not in selected_game:
    st.subheader(f"Player Props for {selected_game}")
    st.write(f"🔍 Debug - API Response Status: 200")
    
    # Fetch active players
    home_team_players = fetch_active_players(selected_game_data["home_team"])
    away_team_players = fetch_active_players(selected_game_data["away_team"])
    all_players = home_team_players + away_team_players
    
    selected_player = st.selectbox("Select a Player", all_players)
    
    if selected_player:
        player_id = get_player_id(selected_player)
        if player_id:
            stats = fetch_player_stats(player_id)
            st.write(f"### Stats for {selected_player}")
            st.write(f"- **Points**: {stats['pts']}")
            st.write(f"- **Assists**: {stats['ast']}")
            st.write(f"- **Rebounds**: {stats['reb']}")
        else:
            st.write("❌ No player stats found.")
    
else:
    st.write("No games available or an error occurred. Try again later.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA prop bettors | Data: balldontlie.io | Odds: Mock (upgrade to real API)")
