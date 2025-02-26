import streamlit as st
import requests
from datetime import datetime

# Title
st.title("NBA Profitable Player Props & Betting Tool")

# Get Today's Date
TODAY_DATE = datetime.today().strftime('%Y-%m-%d')

# Function to Fetch NBA Games for Today
@st.cache_data
def get_nba_games():
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={TODAY_DATE}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "events" in data and data["events"]:
                games = [
                    {
                        "matchup": f"{game['competitions'][0]['competitors'][0]['team']['displayName']} vs {game['competitions'][0]['competitors'][1]['team']['displayName']}",
                        "team1": game['competitions'][0]['competitors'][0]['team']['displayName'],
                        "team2": game['competitions'][0]['competitors'][1]['team']['displayName'],
                        "game_id": game["id"]
                    }
                    for game in data['events']
                ]
                return games
        return []
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return []

# Function to Fetch Player Props Based on More Reliable Source
@st.cache_data
def get_player_props(team_name):
    try:
        url = "https://stats.nba.com/stats/leaguedashplayerstats?Season=2023-24&SeasonType=Regular%20Season&PerMode=PerGame"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nba.com/stats/"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            players_props = []
            headers = data["resultSets"][0]["headers"]
            stats = data["resultSets"][0]["rowSet"]
            for row in stats:
                player_data = dict(zip(headers, row))
                if team_name in player_data.get("TEAM_NAME", ""):
                    players_props.append({
                        "player": player_data["PLAYER_NAME"],
                        "team": player_data["TEAM_NAME"],
                        "points": f"Projected Over {player_data.get('PTS', 'N/A')} Points",
                        "rebounds": f"Projected Over {player_data.get('REB', 'N/A')} Rebounds",
                        "assists": f"Projected Over {player_data.get('AST', 'N/A')} Assists"
                    })
            return players_props if players_props else []  # Ensure list is returned
    except Exception as e:
        st.error(f"Failed to fetch player props: {e}")
        return []  # Prevent crashes by returning an empty list

# Display NBA Games on the Left
st.sidebar.title("Today's NBA Games")
nba_games = get_nba_games()
selected_game = None
if nba_games:
    selected_game = st.sidebar.selectbox("Select a Game:", nba_games, format_func=lambda x: x["matchup"])
else:
    st.sidebar.write("No games found for today")

# Display Player Props for Selected Game
if selected_game:
    st.subheader(f"Player Props for {selected_game['matchup']}")
    st.write(f"Fetching data for: {selected_game['team1']} and {selected_game['team2']}")  # Debugging output
    player_props = get_player_props(selected_game["team1"])
    player_props += get_player_props(selected_game["team2"])
    
    if player_props:
        for prop in player_props:
            st.write(f"**{prop['player']} ({prop['team']})**")
            st.write(f"- {prop['points']}")
            st.write(f"- {prop['rebounds']}")
            st.write(f"- {prop['assists']}")
            st.write("---")
    else:
        st.write("No player props found for this game")

# User Input - Sportsbook Odds for Selected Player
st.subheader("Compare with Sportsbook Lines")
selected_player = st.selectbox("Select a Player to Compare:", [p['player'] for p in player_props] if player_props else [])
if selected_player:
    sportsbook_points = st.number_input("Enter Sportsbook Line for Points:", value=0.0)
    sportsbook_rebounds = st.number_input("Enter Sportsbook Line for Rebounds:", value=0.0)
    sportsbook_assists = st.number_input("Enter Sportsbook Line for Assists:", value=0.0)
    
    player_data = next((p for p in player_props if p['player'] == selected_player), None)
    if player_data:
        def compare_prop(sportsbook_line, projected):
            projected_value = float(projected.split()[-2]) if projected.split()[-2].replace('.', '', 1).isdigit() else 0
            return "BET OVER" if sportsbook_line < projected_value else "NO BET"
        
        st.write(f"**Recommendation for {selected_player}:**")
        st.write(f"- Points: {compare_prop(sportsbook_points, player_data['points'])}")
        st.write(f"- Rebounds: {compare_prop(sportsbook_rebounds, player_data['rebounds'])}")
        st.write(f"- Assists: {compare_prop(sportsbook_assists, player_data['assists'])}")
