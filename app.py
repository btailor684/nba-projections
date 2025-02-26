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

# Function to Fetch Profitable Player Props
@st.cache_data
def get_profitable_props():
    try:
        # Placeholder logic: Replace with actual API call for player props
        profitable_props = [
            {"player": "LeBron James", "team": "Lakers", "prop": "Over 27.5 Points"},
            {"player": "Stephen Curry", "team": "Warriors", "prop": "Over 4.5 Threes"},
            {"player": "Nikola Jokic", "team": "Nuggets", "prop": "Over 9.5 Assists"},
            {"player": "Luka Doncic", "team": "Mavericks", "prop": "Over 8.5 Rebounds"},
        ]
        return profitable_props
    except Exception as e:
        st.error(f"Failed to fetch profitable props: {e}")
        return []

# Display Profitable Player Props
st.subheader("Profitable Player Props for Today")
profitable_props = get_profitable_props()
selected_prop = None
if profitable_props:
    selected_prop = st.selectbox("Select a Player Prop to Compare with Sportsbook:", [
        f"{prop['player']} ({prop['team']}) - {prop['prop']}" for prop in profitable_props
    ])
else:
    st.write("No profitable props found")

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
