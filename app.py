import streamlit as st
import requests
from datetime import datetime, timedelta

# Title
st.title("NBA Profitable Player Props & Betting Tool")

# Function to Fetch NBA Games for Today
@st.cache_data
def get_nba_games():
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "events" in data and data["events"]:
                games = [
                    {
                        "matchup": f"{game['competitions'][0]['competitors'][0]['team']['displayName']} vs {game['competitions'][0]['competitors'][1]['team']['displayName']}",
                        "team1": game['competitions'][0]['competitors'][0]['team']['displayName'],
                        "team2": game['competitions'][0]['competitors'][1]['team']['displayName'],
                    }
                    for game in data['events']
                ]
                return games
        return []
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return []

# Function to Fetch Player Stats from an Alternative Reliable Source
@st.cache_data
def get_player_trends(player_name):
    try:
        url = f"https://api.sportsdata.io/v3/nba/stats/json/PlayerGameStatsByDate/{datetime.today().strftime('%Y-%m-%d')}?key=YOUR_SPORTSDATA_API_KEY"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            player_data = next((p for p in data if p["Name"] == player_name), None)
            if player_data:
                return {
                    "points": player_data["Points"],
                    "rebounds": player_data["Rebounds"],
                    "assists": player_data["Assists"]
                }
        return None
    except Exception as e:
        st.error(f"Failed to fetch player stats: {e}")
        return None

# Function to Generate Profitable Player Props
@st.cache_data
def get_profitable_props():
    props = []
    for game in get_nba_games():
        for team in [game["team1"], game["team2"]]:
            url = f"https://api.sportsdata.io/v3/nba/scores/json/PlayersBasic/{team.replace(' ', '')}?key=YOUR_SPORTSDATA_API_KEY"
            response = requests.get(url)
            if response.status_code == 200:
                team_data = response.json()
                for player in team_data[:4]:  # Pick top 4 key players
                    stats = get_player_trends(player["Name"])
                    if stats:
                        props.append({
                            "player": player["Name"],
                            "team": team,
                            "prop": f"Over {round(stats['points']+2,1)} Points" if stats["points"] else "Over 20.5 Points",
                            "prop_reb": f"Over {round(stats['rebounds']+1,1)} Rebounds" if stats["rebounds"] else "Over 5.5 Rebounds",
                            "prop_ast": f"Over {round(stats['assists']+1,1)} Assists" if stats["assists"] else "Over 4.5 Assists"
                        })
    return props

# Display NBA Games on the Left
st.sidebar.title("Today's NBA Games")
nba_games = get_nba_games()
if nba_games:
    for game in nba_games:
        st.sidebar.write(game["matchup"])
else:
    st.sidebar.write("No games found for today")

# Display Profitable Player Props
st.subheader("Profitable Player Props for Today's Games")
player_props = get_profitable_props()
selected_prop = None
if player_props:
    selected_prop = st.selectbox("Select a Player Prop to Compare with Sportsbook:", [
        f"{prop['player']} ({prop['team']}) - {prop['prop']}" for prop in player_props
    ])
else:
    st.write("No player props found")

# User Input - Sportsbook Odds for Selected Prop
if selected_prop:
    st.subheader("Compare with Sportsbook Lines")
    sportsbook_line = st.number_input("Enter Sportsbook Line for Selected Prop:", value=0.0)
    
    # Extract Expected Projection
    expected_projection = float(selected_prop.split()[-2])
    
    # Basic Comparison Logic
    recommended_bet = "BET OVER" if sportsbook_line < expected_projection else "NO BET"
    
    st.write(f"Recommendation: **{recommended_bet}**")
