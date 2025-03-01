import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Key (Ensure this remains set at all times)
API_KEY = "YOUR_API_KEY_HERE"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# Function to fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Function to fetch active players for a selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players/active?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Function to fetch recent player game logs
def fetch_recent_player_game_logs(player_id):
    url = f"{BASE_URL}/stats?player_ids[]={player_id}&per_page=10"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Function to fetch season averages
def fetch_season_averages(player_id):
    url = f"{BASE_URL}/season_averages/general?season=2024&season_type=regular&type=base&player_ids[]={player_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get("data", [])
        return data[0] if data else None
    return None

# Function to fetch betting odds
def fetch_betting_odds(game_id):
    url = f"{BASE_URL}/odds?game_id={game_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games, players, and stats.")

games = fetch_games()

game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_id = game_data["id"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    
    st.title("🏀 PropEdge NBA")
    st.write("View today's NBA games, players, stats, and betting odds.")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")
    
    # Fetching players from both teams
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    
    players = players_home + players_away
    
    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")
            
            # Fetch Player Season Averages
            season_avg = fetch_season_averages(player_id)
            if season_avg:
                st.markdown(f"## 📊 Season Averages for {selected_player}")
                st.table(pd.DataFrame([season_avg]))
            else:
                st.warning("⚠️ No season averages available for this player.")
            
            # Fetch Recent Game Logs
            game_logs = fetch_recent_player_game_logs(player_id)
            if game_logs:
                st.markdown(f"## 📉 Last 10 Games for {selected_player}")
                df_logs = pd.DataFrame(game_logs)[["game", "pts", "reb", "ast", "min", "fg_pct"]]
                df_logs = df_logs.rename(columns={"pts": "Points", "reb": "Rebounds", "ast": "Assists", "min": "Minutes", "fg_pct": "FG%"})
                df_logs["Date"] = df_logs["game"].apply(lambda g: g["date"])
                df_logs["Opponent"] = df_logs["game"].apply(lambda g: g["visitor_team"]["full_name"] if g["home_team"]["id"] == home_team["id"] else g["home_team"]["full_name"])
                df_logs = df_logs[["Date", "Opponent", "Points", "Rebounds", "Assists", "Minutes", "FG%"]]
                st.table(df_logs)
            else:
                st.warning("⚠️ No game logs available for this player.")
            
            # Fetch Betting Odds
            odds_data = fetch_betting_odds(game_id)
            if odds_data:
                st.markdown(f"## 💰 Betting Odds for {selected_game}")
                df_odds = pd.DataFrame(odds_data)[["vendor", "spread", "over_under"]]
                df_odds = df_odds.rename(columns={"vendor": "Sportsbook", "spread": "Spread", "over_under": "O/U"})
                st.table(df_odds)
            else:
                st.warning("⚠️ No betting odds available for this game.")
    
    else:
        st.warning("⚠️ No active players found for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
