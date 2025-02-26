import streamlit as st
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

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

# Function to Scrape Player Props from Sportsbooks (DraftKings & BetMGM)
def scrape_sportsbook_props():
    props = []
    try:
        # DraftKings Scraping
        dk_url = "https://sportsbook.draftkings.com/leagues/basketball/nba"
        headers = {"User-Agent": "Mozilla/5.0"}
        dk_response = requests.get(dk_url, headers=headers)
        if dk_response.status_code == 200:
            dk_soup = BeautifulSoup(dk_response.text, 'html.parser')
            for item in dk_soup.find_all("div", class_="sportsbook-event-accordion__title"):
                prop_name = item.get_text(strip=True)
                props.append(prop_name)
    except Exception as e:
        st.error(f"Failed to fetch DraftKings props: {e}")
    
    try:
        # BetMGM Scraping
        mgm_url = "https://sports.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-600036"
        mgm_response = requests.get(mgm_url, headers=headers)
        if mgm_response.status_code == 200:
            mgm_soup = BeautifulSoup(mgm_response.text, 'html.parser')
            for item in mgm_soup.find_all("span", class_="option-name"):
                prop_name = item.get_text(strip=True)
                props.append(prop_name)
    except Exception as e:
        st.error(f"Failed to fetch BetMGM props: {e}")
    
    return props[:10]  # Return top 10 most popular props

# Function to Generate Profitable Player Props Based on Today's Games
@st.cache_data
def get_profitable_props():
    props = []
    for game in get_nba_games():
        for team in [game["team1"], game["team2"]]:
            scraped_props = scrape_sportsbook_props()
            for prop in scraped_props:
                props.append({
                    "player": prop.split(" ")[0],
                    "team": team,
                    "prop": prop
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
st.subheader("Top 5 Profitable Player Props for Today")
player_props = get_profitable_props()
selected_prop = None
if player_props:
    selected_prop = st.selectbox("Select a Player Prop to Compare with Sportsbook:", [
        f"{prop['player']} ({prop['team']}) - {prop['prop']}" for prop in player_props[:5]
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
