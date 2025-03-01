import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ✅ API Key (DO NOT REMOVE THIS)
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# ✅ Function to fetch today's NBA games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    st.error(f"Failed to fetch games: {response.json()}")
    return []

# ✅ Function to fetch active players for a selected game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players/active?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    st.error(f"Failed to fetch players: {response.json()}")
    return []

# ✅ FIXED: Function to fetch player season averages (Corrected Player ID Format)
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages/general?season=2024&season_type=regular&type=base&player_ids[]={player_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        stats = response.json().get("data", [])
        return stats[0] if stats else None
    st.error(f"Failed to fetch season averages: {response.json()}")
    return None

# ✅ FIXED: Function to fetch last 10 game logs for a player (Corrected Opponent Data)
def fetch_recent_player_game_logs(player_id):
    url = f"{BASE_URL}/stats?player_ids[]={player_id}&per_page=10&sort=game.date&order=desc"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get("data", [])
        cleaned_logs = []
        for game in data:
            home_team = game["game"]["home_team"]
            visitor_team = game["game"]["visitor_team"]
            opponent = visitor_team["full_name"] if game["game"]["home_team_id"] == home_team["id"] else home_team["full_name"]
            
            game_data = {
                "Date": game["game"]["date"],
                "Opponent": opponent,
                "Points": game.get("pts", "N/A"),
                "Rebounds": game.get("reb", "N/A"),
                "Assists": game.get("ast", "N/A"),
                "Minutes": game.get("min", "N/A"),
                "FG%": game.get("fg_pct", "N/A"),
            }
            cleaned_logs.append(game_data)
        return cleaned_logs
    st.error(f"Failed to fetch game logs: {response.json()}")
    return []

# ✅ Function to fetch betting odds (FanDuel only)
def fetch_betting_odds(game_id):
    url = f"{BASE_URL}/odds?game_id={game_id}&vendor=FanDuel"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        odds_data = response.json().get("data", [])
        if odds_data:
            selected_odds = {
                "Spread": odds_data[0].get("spread", "N/A"),
                "Spread Odds": odds_data[0].get("spread_odds", "N/A"),
                "Over/Under": odds_data[0].get("over_under", "N/A"),
                "Over/Under Odds": odds_data[0].get("over_under_odds", "N/A"),
            }
            return selected_odds
    st.error(f"Failed to fetch betting odds: {response.json()}")
    return {}

# ✅ Streamlit UI
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games, players, stats, and betting odds.")

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
    
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    
    players = players_home + players_away
    
    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))
        
        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")
            
            # ✅ Display Season Averages
            season_avg = fetch_player_season_averages(player_id)
            if season_avg:
                st.subheader(f"📊 Season Averages for {selected_player}")
                st.table(pd.DataFrame([season_avg]))
            else:
                st.warning("⚠️ No season averages available for this player.")
            
            # ✅ Display Last 10 Games
            game_logs = fetch_recent_player_game_logs(player_id)
            if game_logs:
                df_logs = pd.DataFrame(game_logs)
                st.subheader(f"📊 Last 10 Games for {selected_player}")
                st.table(df_logs)
            else:
                st.warning("⚠️ No recent game logs available for this player.")
    else:
        st.warning("⚠️ No active players found for this game.")
    
    # ✅ Display Betting Odds (FanDuel)
    betting_odds = fetch_betting_odds(game_id)
    if betting_odds:
        st.subheader(f"📈 Betting Odds for {selected_game}")
        df_odds = pd.DataFrame([betting_odds])
        st.table(df_odds)
    else:
        st.warning("⚠️ No betting odds available for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
