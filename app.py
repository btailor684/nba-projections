import streamlit as st
import requests
from datetime import datetime

# API Configuration
API_BASE_URL = "https://api.balldontlie.io/v1"
API_KEY = "your_api_key_here"  # Replace with your actual API key
HEADERS = {"Authorization": API_KEY}

# Fetch today's games
def get_todays_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"{API_BASE_URL}/games?start_date={today}&end_date={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# Fetch active players for a given team
def get_active_players(team_id):
    url = f"{API_BASE_URL}/players?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# Fetch player stats
def get_player_stats(player_id):
    season = 2024  # Ensure the season is current
    url = f"{API_BASE_URL}/season_averages?season={season}&player_ids={player_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        stats = response.json().get("data", [])
        return stats[0] if stats else None
    return None

# Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.markdown("Select a Game")

games = get_todays_games()
game_options = {f"{g['home_team']['full_name']} vs {g['visitor_team']['full_name']}": g for g in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()) if game_options else ["No games available"])

if selected_game in game_options:
    game = game_options[selected_game]
    st.title("🏀 PropEdge NBA")
    st.markdown("View today's NBA games, players, and stats.")
    
    st.subheader(f"Players for {selected_game}")
    game_time = datetime.strptime(game["date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%B %d, %Y - %I:%M %p ET")
    st.markdown(f"⏳ **Game Time:** {game_time}")
    
    team_ids = [game["home_team"]["id"], game["visitor_team"]["id"]]
    players = [player for team_id in team_ids for player in get_active_players(team_id)]
    
    if players:
        player_names = {f"{p['first_name']} {p['last_name']}": p["id"] for p in players}
        selected_player = st.selectbox("Select a Player", list(player_names.keys()))
        
        if selected_player:
            player_id = player_names[selected_player]
            st.markdown(f"🔍 **Fetching stats for:** **{selected_player} (ID: {player_id})**")
            
            stats = get_player_stats(player_id)
            if stats:
                st.markdown("## Player Stats")
                st.write(stats)
            else:
                st.warning("⚠️ No stats available for this player.")
    else:
        st.warning("⚠️ No active players found for this game.")

st.markdown("---")
st.markdown("Built with ❤️ for NBA fans | Data: balldontlie.io")
