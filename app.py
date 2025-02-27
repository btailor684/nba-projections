import streamlit as st
import requests
from datetime import datetime

# API Configuration
API_KEY = "your_api_key_here"
HEADERS = {"Authorization": API_KEY}

# Streamlit UI Enhancements
st.set_page_config(page_title="PropEdge NBA", page_icon="🏀", layout="wide")

# Sidebar UI
st.sidebar.title("📅 Today's NBA Games")
st.sidebar.markdown("View today's NBA games, players, and stats.")

# --- Fetch Daily NBA Games ---
def fetch_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.balldontlie.io/v1/games?start_date={today}&end_date={today}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                    "home_team": game["home_team"]["id"],
                    "away_team": game["visitor_team"]["id"],
                    "date": game["date"]
                }
                for game in data["data"]
            ]
        else:
            return []
    except Exception as e:
        return []

# --- Fetch Active Players for a Team ---
def fetch_active_players(team_id):
    url = f"https://api.balldontlie.io/v1/players/active?team_ids={team_id}&per_page=100"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "id": player["id"],
                    "name": f"{player['first_name']} {player['last_name']}",
                    "position": player["position"],
                    "team": player["team"]["full_name"],
                }
                for player in data["data"]
            ]
        else:
            return []
    except Exception as e:
        return []

# --- Fetch Player Stats ---
def fetch_player_stats(player_id):
    url = f"https://api.balldontlie.io/v1/season_averages?season=2024&player_id={player_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                return data["data"][0]  # Return stats
            else:
                return None
        else:
            return None
    except Exception as e:
        return None

# --- Streamlit App Layout ---
st.markdown("# 🏀 PropEdge NBA")
st.markdown("View today's NBA games, players, and stats.")

# Fetch NBA games
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)

# Get selected game data
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

if selected_game_data:
    # Display game title
    st.markdown(f"## Players for **{selected_game}**")
    game_time = datetime.strptime(selected_game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    st.markdown(f"🕒 **Game Time:** **{game_time}**")

    # Fetch and display active players
    home_team_players = fetch_active_players(selected_game_data["home_team"])
    away_team_players = fetch_active_players(selected_game_data["away_team"])
    all_players = home_team_players + away_team_players

    if all_players:
        st.markdown("### Players in this game:")
        player_names = [player["name"] for player in all_players]
        selected_player = st.selectbox("Select a Player", player_names)

        # Find player ID
        selected_player_data = next((player for player in all_players if player["name"] == selected_player), None)

        if selected_player_data:
            st.markdown(f"🔍 **Fetching stats for:** **{selected_player} (ID: {selected_player_data['id']})**")

            # Fetch player stats
            player_stats = fetch_player_stats(selected_player_data["id"])

            if player_stats:
                st.markdown("### 📊 Player Stats")
                st.write(f"**Points per Game:** {player_stats.get('pts', 'N/A')}")
                st.write(f"**Assists per Game:** {player_stats.get('ast', 'N/A')}")
                st.write(f"**Rebounds per Game:** {player_stats.get('reb', 'N/A')}")
            else:
                st.warning("⚠️ No stats available for this player.")
    else:
        st.warning("⚠️ No active players found for this game.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for NBA fans | Data: balldontlie.io")
