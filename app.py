import streamlit as st
import requests
from datetime import datetime

# API Key for balldontlie.io
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}  # Use correct authentication method

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
        st.write(f"API Response Status: {response.status_code}")  # Debugging
        st.write(f"API Response Content: {response.text}")  # Debugging

        if response.status_code == 200:
            data = response.json()
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
        return [{"matchup": f"API Error (Status: {response.status_code})", "home_team": "", "away_team": ""}]
    
    except Exception as e:
        return [{"matchup": f"Error: {str(e)}", "home_team": "", "away_team": ""}]

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
