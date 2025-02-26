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
    "CHA": {"pts_allowed": 26.5, "reb_allowed
