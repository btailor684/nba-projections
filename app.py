import streamlit as st
import requests
from datetime import datetime

# App Title and Description
st.title("PropEdge NBA")
st.markdown("Your daily edge for NBA player prop bets. Get projections and recommendations for points, assists, and rebounds.")

# --- Fetch Daily NBA Games ---
def fetch_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://www.balldontlie.io/api/v1/games?start_date={today}&end_date={today}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            games = [
                {
                    "matchup": f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}",
                    "home_team": game['home_team']['abbreviation'],
                    "away_team": game['visitor_team']['abbreviation']
                }
                for game in data['data']
            ]
            return games if games else [{"matchup": "No games found today", "home_team": "", "away_team": ""}]
        else:
            return [{"matchup": f"API Error (Status: {response.status_code})", "home_team": "", "away_team": ""}]
    except Exception as e:
        return [{"matchup": f"Error: {str(e)}", "home_team": "", "away_team": ""}]

# --- Fetch Player Stats ---
def get_player_id(player_name):
    url = "https://www.balldontlie.io/api/v1/players"
    try:
        response = requests.get(url, params={"search": player_name, "per_page": 10})
        if response.status_code == 200 and response.json()["data"]:
            return response.json()["data"][0]["id"]
        return None
    except:
        return None

def fetch_player_stats(player_id):
    url = f"https://www.balldontlie.io/api/v1/season_averages?season=2024&player_ids[]={player_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200 and response.json()["data"]:
            stats = response.json()["data"][0]
            return {
                "pts": stats["pts"],
                "ast": stats["ast"],
                "reb": stats["reb"],
                "min": float(stats["min"].split(":")[0])  # Convert "34:30" to 34.0
            }
        return {"pts": 0, "ast": 0, "reb": 0, "min": 0}
    except:
        return {"pts": 0, "ast": 0, "reb": 0, "min": 0}

# --- Mock Team Defense Data (for simplicity) ---
mock_defense = {
    "LAL": {"pts_allowed": 25.0, "reb_allowed": 10.0, "ast_allowed": 6.0},  # Lakers
    "CHA": {"pts_allowed": 26.5, "reb_allowed": 11.0, "ast_allowed": 7.0},  # Hornets
    "BKN": {"pts_allowed": 24.0, "reb_allowed": 9.5, "ast_allowed": 5.5},   # Nets
    "PHI": {"pts_allowed": 23.5, "reb_allowed": 9.0, "ast_allowed": 5.0}    # 76ers
}

# --- Mock Sportsbook Odds (replace with real API later) ---
mock_odds = {
    "LeBron James": {"pts": 24.5, "ast": 7.5, "reb": 8.5},
    "Anthony Davis": {"pts": 27.0, "ast": 2.5, "reb": 11.5},
    "LaMelo Ball": {"pts": 22.5, "ast": 8.0, "reb": 6.5},
    "Kevin Durant": {"pts": 28.0, "ast": 4.5, "reb": 7.0}
}

# --- Projection Logic ---
def calculate_projections(stats, opp_defense):
    proj_pts = stats["pts"] * 0.7 + stats["min"] * 0.2 - opp_defense["pts_allowed"] * 0.1
    proj_ast = stats["ast"] * 0.75 + stats["min"] * 0.15 - opp_defense["ast_allowed"] * 0.1
    proj_reb = stats["reb"] * 0.8 + stats["min"] * 0.1 + opp_defense["reb_allowed"] * 0.1
    return {
        "pts": max(round(proj_pts, 1), 0),
        "ast": max(round(proj_ast, 1), 0),
        "reb": max(round(proj_reb, 1), 0)
    }

# --- Recommendation Logic ---
def recommend_bet(projection, line):
    edge = projection - line
    if edge >= 2.0:
        return "Good Play ✅"
    elif edge <= -2.0:
        return "Avoid ❌"
    else:
        return "Neutral"

# --- Sidebar: Display Games ---
st.sidebar.title("Today's NBA Games")
games = fetch_nba_games()
game_options = [game["matchup"] for game in games]
selected_game = st.sidebar.selectbox("Select a Game", game_options)
selected_game_data = next((game for game in games if game["matchup"] == selected_game), None)

# --- Main Content ---
if selected_game_data and "No games" not in selected_game and "Error" not in selected_game:
    st.subheader(f"Player Props for {selected_game}")
    
    team_players = {
        "LAL": ["LeBron James", "Anthony Davis"],
        "CHA": ["LaMelo Ball"],
        "BKN": ["Kevin Durant"],
        "PHI": []
    }
    
    home_team_players = team_players.get(selected_game_data["home_team"], [])
    away_team_players = team_players.get(selected_game_data["away_team"], [])
    all_players = home_team_players + away_team_players

    if all_players:
        table_data = []
        for player in all_players:
            player_id = get_player_id(player)
            stats = fetch_player_stats(player_id) if player_id else {"pts": 0, "ast": 0, "reb": 0, "min": 0}
            opp_team = selected_game_data["away_team"] if player in home_team_players else selected_game_data["home_team"]
            opp_defense = mock_defense.get(opp_team, {"pts_allowed": 25.0, "reb_allowed": 10.0, "ast_allowed": 6.0})
            projections = calculate_projections(stats, opp_defense)
            odds = mock_odds.get(player, {"pts": 0, "ast": 0, "reb": 0})
            table_data.append([player, "PTS", projections["pts"], odds["pts"], recommend_bet(projections["pts"], odds["pts"])])
        st.table(table_data)
