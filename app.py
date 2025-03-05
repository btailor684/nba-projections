import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# API Key (DO NOT REMOVE OR ALTER)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

### 🔹 FUNCTION: Fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

### 🔹 FUNCTION: Fetch active players for the selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players/active?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

### 🔹 FUNCTION: Fetch season averages for a player
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages?season=2024&player_ids[]={player_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json().get("data", [])

        if data:
            return data[0]  # Return first entry if available

    return None  # Return None if no data is found

### 🔹 FUNCTION: Fetch last 10 games for a player (most recent games played)
def fetch_recent_player_game_logs(player_id):
    url = f"{BASE_URL}/stats?player_ids[]={player_id}&per_page=10&sort=game.date&order=desc"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        game_logs = response.json().get("data", [])

        # Extract relevant fields
        df_logs = pd.DataFrame(game_logs)
        if not df_logs.empty:
            df_logs = df_logs[["game", "pts", "reb", "ast", "min", "fg_pct"]]
            df_logs.rename(columns={
                "game": "Date",
                "pts": "Points",
                "reb": "Rebounds",
                "ast": "Assists",
                "min": "Minutes",
                "fg_pct": "FG%"
            }, inplace=True)

            # Convert date format
            df_logs["Date"] = df_logs["Date"].apply(lambda x: x["date"][:10])
            
            return df_logs

    return None  # Return None if no data found

### 🔹 FUNCTION: Fetch betting odds for the selected game
def fetch_betting_odds(game_id):
    url = f"{BASE_URL}/odds?game_id={game_id}&vendor=FanDuel"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        odds_data = response.json().get("data", [])
        
        # Extract relevant odds data
        if odds_data:
            best_odds = {
                "Spread": odds_data[0].get("spread", "N/A"),
                "Spread Odds": odds_data[0].get("spread_odds", "N/A"),
                "Over/Under": odds_data[0].get("over_under", "N/A"),
                "Over/Under Odds": odds_data[0].get("over_under_odds", "N/A")
            }
            return pd.DataFrame([best_odds])  # Return as DataFrame

    return None  # Return None if no data is found

# 🎨 Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games, players, stats, and betting odds.")

# Fetch Games
games = fetch_games()

game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")
    game_id = game_data["id"]
    
    st.title("🏀 PropEdge NBA")
    st.write("View today's NBA games, players, stats, and betting odds.")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")
    
    # Fetch Active Players
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    players = players_home + players_away

    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")
            
            # Fetch Season Averages
            season_avg = fetch_player_season_averages(player_id)
            if season_avg:
                st.subheader(f"📊 Season Averages for {selected_player}")

                stats_to_display = {
                    "Points": season_avg.get("pts", "N/A"),
                    "Rebounds": season_avg.get("reb", "N/A"),
                    "Assists": season_avg.get("ast", "N/A"),
                    "Field Goal %": season_avg.get("fg_pct", "N/A"),
                    "Minutes": season_avg.get("min", "N/A"),
                }
                df_season_avg = pd.DataFrame([stats_to_display])
                st.table(df_season_avg)
            else:
                st.warning("⚠️ No season averages available for this player.")

            # Fetch Last 10 Games
            game_logs = fetch_recent_player_game_logs(player_id)
            if game_logs is not None:
                st.subheader(f"📊 Last 10 Games for {selected_player}")
                st.table(game_logs)
            else:
                st.warning("⚠️ No recent game logs available for this player.")

    else:
        st.warning("⚠️ No active players found for this game.")
    
    # Fetch Betting Odds
    betting_odds = fetch_betting_odds(game_id)
    if betting_odds is not None:
        st.subheader(f"📈 Betting Odds for {selected_game}")
        st.table(betting_odds)
    else:
        st.warning("⚠️ No betting odds available for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
