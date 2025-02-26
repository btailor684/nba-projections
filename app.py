import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io (Ensure it's a valid, paid API key)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}  # Use correct authentication method

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

        # **Debugging: Print API Response**
        st.write(f"🔍 Debug - API Response Status: {response.status_code}")  
        if response.status_code != 200:
            st.write(f"⚠️ Debug - API Response Content: {response.text}")  

        # **Check if API Response is Valid JSON**
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            return [{"matchup": f"Error: Non-JSON response received", "home_team": "", "away_team": ""}]

        # **Check if 'data' Key Exists**
        if "data" in data and data["data"]:
            games = [
                {
                    "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                    "home_team": game['home_team']['abbreviation'],
                    "away_team": game['visitor_team']['abbreviation']
                }
                for game in data["data"]
            ]
            return games if games else [{"matchup": "No games found today", "home_team": "", "away_team": ""}]
        else:
            return [{"matchup": "No games available", "home_team": "", "away_team": ""}]

    except requests.exceptions.RequestException as e:
        return [{"matchup": f"⚠️ Error: {str(e)}", "home_team": "", "away_team": ""}]

# --- Fetch Player Stats ---
def get_player_id(player_name):
    url = "https://api.balldontlie.io/v1/players"
    try:
        response = requests.get(url, headers=HEADERS, params={"search": player_name, "per_page": 1})
        if response.status_code == 200 and "data" in response.json() and response.json()["data"]:
            return response.json()["data"][0].get("id")
        return None
    except requests.exceptions.RequestException:
        return None

def fetch_player_stats(player_id):
    url = "https://api.balldontlie.io/v1/season_averages"
    params = {"season": 2024, "player_ids[]": player_id}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200 and "data" in response.json() and response.json()["data"]:
            stats = response.json()["data"][0]
            return {
                "pts": stats.get("pts", 0),
                "ast": stats.get("ast", 0),
                "reb": stats.get("reb", 0),
                "min": float(stats.get("min", "0").split(":")[0])  # Convert "34:30" to 34.0
            }
        return {"pts": 0, "ast": 0, "reb": 0, "min": 0}
    except requests.exceptions.RequestException:
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
    st.write(f"Debug: Selected Game Data - {selected_game_data}")
else:
    st.write("No games available or an error occurred. Try again later.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA prop bettors | Data: balldontlie.io | Odds: Mock (upgrade to real API)")
