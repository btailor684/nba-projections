import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Key (Ensure this remains set at all times)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# Function to fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?start_date={today}&end_date={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# Function to fetch active players for a selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players?team_ids[]={team_id}&per_page=50"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# ✅ **Fixed Season Averages Fetching**
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages/general?season=2024&season_type=regular&type=base&player_ids[]={player_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        stats = response.json().get("data", [])
        return stats[0] if stats else None
    return None

# ✅ **Fixed Last 10 Game Logs & Opponent Name Extraction**
def fetch_recent_player_game_logs(player_id):
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/stats?player_ids[]={player_id}&seasons[]=2024&per_page=50"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        games = response.json().get("data", [])
        completed_games = [
            game for game in games 
            if "game" in game and game["game"].get("date") < today
        ]

        # Sort games by most recent date
        completed_games.sort(key=lambda x: x["game"]["date"], reverse=True)

        for game in completed_games:
            game_info = game.get("game", {})
            home_team_id = game_info.get("home_team_id")
            visitor_team_id = game_info.get("visitor_team_id")

            if home_team_id and visitor_team_id:
                game["opponent"] = game_info["visitor_team"]["full_name"] if home_team_id == game["player"]["team_id"] else game_info["home_team"]["full_name"]
            else:
                game["opponent"] = "Unknown"

        return completed_games[:10]
    return []

# Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games and players.")

games = fetch_games()
game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    
    st.title("🏀 PropEdge NBA")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")
    
    # Fetch players from both teams
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    players = players_home + players_away
    
    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player for player in players}
        selected_player_name = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player_name:
            player_info = player_dict[selected_player_name]
            player_id = player_info["id"]
            
            # Display Basic Info
            st.subheader(f"📊 Player Details for: {selected_player_name}")
            st.write(f"- **Position:** {player_info.get('position', 'N/A')}")
            st.write(f"- **Height:** {player_info.get('height', 'N/A')}")
            st.write(f"- **Weight:** {player_info.get('weight', 'N/A')}")
            st.write(f"- **College:** {player_info.get('college', 'N/A')}")
            st.write(f"- **Country:** {player_info.get('country', 'N/A')}")

            # ✅ **Fixed Season Averages Retrieval**
            st.subheader(f"📈 Season Averages for {selected_player_name}")
            season_averages = fetch_player_season_averages(player_id)
            
            if season_averages:
                season_df = pd.DataFrame([season_averages])
                st.table(season_df)
            else:
                st.warning("⚠️ No season averages available for this player.")

            # Fetch and Display Last 10 Completed Games
            st.subheader(f"📊 Last 10 Games for {selected_player_name}")
            game_logs = fetch_recent_player_game_logs(player_id)
            
            if game_logs:
                # Create a DataFrame with the latest stats
                game_log_df = pd.DataFrame([
                    {
                        "Date": game["game"]["date"],
                        "Opponent": game.get("opponent", "Unknown"),
                        "Points": game.get("pts", 0),
                        "Rebounds": game.get("reb", 0),
                        "Assists": game.get("ast", 0),
                        "Minutes": game.get("min", "N/A"),
                        "FG%": round((game["fg_pct"] * 100), 1) if game.get("fg_pct") is not None else "N/A"
                    } for game in game_logs
                ])
                
                # Show in table
                st.table(game_log_df)
            else:
                st.warning("⚠️ No recent game stats available for this player.")
    else:
        st.warning("⚠️ No active players found for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
