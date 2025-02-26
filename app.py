import streamlit as st
import requests
from datetime import datetime

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
                        "game_id": game['id']
                    }
                    for game in data['events']
                ]
                return games
        return []
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return []

# Display NBA Games on the Left
st.sidebar.title("Today's NBA Games")
nba_games = get_nba_games()
if nba_games:
    for game in nba_games:
        st.sidebar.write(game["matchup"])
else:
    st.sidebar.write("No games found for today")

# Function to Fetch Player Props for Today's Games
@st.cache_data
def get_player_props():
    try:
        # Placeholder logic: Replace with actual API call for player props
        props = []
        for game in nba_games:
            team1, team2 = game["matchup"].split(" vs ")
            props.extend([
                {"player": f"Top Scorer {team1}", "team": team1, "prop": "Over 25.5 Points"},
                {"player": f"Top Rebounder {team1}", "team": team1, "prop": "Over 9.5 Rebounds"},
                {"player": f"Top Assister {team1}", "team": team1, "prop": "Over 7.5 Assists"},
                {"player": f"Best 3PT Shooter {team1}", "team": team1, "prop": "Over 3.5 Threes"},
                {"player": f"Top Scorer {team2}", "team": team2, "prop": "Over 25.5 Points"},
                {"player": f"Top Rebounder {team2}", "team": team2, "prop": "Over 9.5 Rebounds"},
                {"player": f"Top Assister {team2}", "team": team2, "prop": "Over 7.5 Assists"},
                {"player": f"Best 3PT Shooter {team2}", "team": team2, "prop": "Over 3.5 Threes"},
            ])
        return props
    except Exception as e:
        st.error(f"Failed to fetch player props: {e}")
        return []

# Display Profitable Player Props
st.subheader("Profitable Player Props for Today's Games")
player_props = get_player_props()
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
    
    # Basic Comparison Logic
    if "Over" in selected_prop:
        recommended_bet = "BET OVER" if sportsbook_line < float(selected_prop.split()[-2]) else "NO BET"
    else:
        recommended_bet = "BET UNDER" if sportsbook_line > float(selected_prop.split()[-2]) else "NO BET"
    
    st.write(f"Recommendation: **{recommended_bet}**")
