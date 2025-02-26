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
    url = "https://api.balldontlie.io/v1/games"
    params = {"start_date": today, "end_date": today, "per_page": 100}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)

        # Debugging
        st.write(f"🔍 Debug - API Response Status: {response.status_code}")
        if response.status_code != 200:
            st.write(f"⚠️ Debug - API Response Content: {response.text}")

        data = response.json()

        if "data" in data and data["data"]:
            games = [
                {
                    "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                    "home_team": game['home_team']['abbreviation'],
                    "home_team_id": game['home_team']['id'],
                    "away_team": game['visitor_team']['abbreviation'],
                    "away_team_id": game['visitor_team']['id']
                }
                for game in data["data"]
            ]
            return games if games else [{"matchup": "No games found today"}]
        else:
            return [{"matchup": "No games available"}]

    except requests.exceptions.RequestException as e:
        return [{"matchup": f"⚠️ Error: {str(e)}"}]

# --- Fetch Players for a Team ---
def fetch_players_by_team(team_id):
    url = "https://api.balldontlie.io/v1/players"
    params = {"team_ids[]": team_id, "per_page": 10}  # Limit to 10 for now

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        if "data" in data:
            return [player["first_name"] + " " + player["last_name"] for player in data["data"]]
        return []
    except requests.exceptions.RequestException:
        return []

# --- Fetch Player Stats ---
def fetch_player_stats(player_name):
    player_url = "https://api.balldontlie.io/v1/players"
    stats_url = "https://api.balldontlie.io/v1/season_averages"

    try:
        # Get Player ID
        response = requests.get(player_url, headers=HEADERS, params={"search": player_name, "per_page": 1})
        data = response.json()
        
        if "data" in data and data["data"]:
            player_id = data["data"][0]["id"]
        else:
            return None

        # Get Player Stats
        response = requests.get(stats_url, headers=HEADERS, params={"season": 2024, "player_ids[]": player_id})
        stats_data = response.json()

        if "data" in stats_data and stats_data["data"]:
            stats = stats_data["data"][0]
            return {
                "pts": stats.get("pts", 0),
                "ast": stats.get("ast", 0),
                "reb": stats.get("reb", 0)
            }
        return None

    except requests.exceptions.RequestException:
        return None

# --- Sidebar: Display Games ---
st.sidebar.title("Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# --- Main Content ---
if selected_game_data and "No games" not in selected_game:
    st.subheader(f"Player Props for {selected_game}")

    # Fetch players from both teams
    home_players = fetch_players_by_team(selected_game_data["home_team_id"])
    away_players = fetch_players_by_team(selected_game_data["away_team_id"])
    all_players = home_players + away_players

    # Allow user to select a player
    selected_player = st.selectbox("Select a Player", all_players)

    # Fetch player stats
    player_stats = fetch_player_stats(selected_player)
    
    if player_stats:
        st.write(f"**Projections for {selected_player}:**")
        st.write(f"📊 Points: {player_stats['pts']}")
        st.write(f"🎯 Assists: {player_stats['ast']}")
        st.write(f"💪 Rebounds: {player_stats['reb']}")
    else:
        st.write("❌ No player stats found.")

else:
    st.write("No games available or an error occurred. Try again later.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA prop bettors | Data: balldontlie.io | Odds: Mock (upgrade to real API)")
