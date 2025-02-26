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
                return games if games else []
        return []
    except Exception as e:
        st.error(f"Error fetching games: {str(e)}")
        return []

# --- Fetch Active Players in Game ---
def fetch_active_players(team_id):
    """Fetches only ACTIVE players for a specific team using the correct endpoint."""
    url = f"https://api.balldontlie.io/v1/players/active"
    params = {"team_ids[]": team_id, "per_page": 100}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        # Debugging response
        st.write(f"🔍 Debug: API Response Status - {response.status_code}")
        st.write(f"🔍 Debug: API URL - {response.url}")

        if response.status_code == 200:
            data = response.json()
            st.write(f"🔍 Debug: API Response Data - {data}")  # Print full response for debugging
            
            players = [f"{player['first_name']} {player['last_name']}" for player in data.get("data", [])]

            # Print players found
            if players:
                st.write(f"✅ Found {len(players)} active players: {players}")
            else:
                st.write("⚠ No active players found in API response.")

            return players
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error fetching active players: {str(e)}")
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
    home_team_players = fetch_active_players(selected_game_data["home_team"])
    away_team_players = fetch_active_players(selected_game_data["away_team"])
    all_players = home_team_players + away_team_players
    
    if all_players:
        st.write("### Players in this game:")
        st.table({"Players": all_players})
    else:
        st.write("⚠ No active players found for this game.")
else:
    st.write("No games available today.")

# Footer
st.markdown("---")
st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
