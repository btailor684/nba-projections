import streamlit as st
import requests
from datetime import datetime

# Title
st.title("NBA Player Projection & Betting Tool")

# Function to Fetch NBA Player Names from a Public API
@st.cache_data
def get_nba_players():
    url = "https://www.balldontlie.io/api/v1/players?per_page=100&page=1"
    players = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            players.extend([f"{player['first_name']} {player['last_name']}" for player in data["data"]])
            url = data.get("meta", {}).get("next_page", None)
        else:
            st.error(f"Error fetching players: {response.status_code}")
            return []
    return players

# Fetch Player List
dynamic_nba_players = get_nba_players()

# User Input - Player Name with Autocomplete
player_name = st.text_input("Enter NBA Player Name")
if player_name:
    matching_players = [p for p in dynamic_nba_players if player_name.lower() in p.lower()]
    if matching_players:
        player_name = st.selectbox("Select a Player", matching_players)
    else:
        st.warning("No matching player found. Try a different name.")
        player_name = None

# User Input - Sportsbook Odds
st.subheader("Enter Sportsbook Over/Under Lines:")
odds_pts = st.number_input("Over/Under Points", value=25.5)
odds_reb = st.number_input("Over/Under Rebounds", value=6.5)
odds_ast = st.number_input("Over/Under Assists", value=5.5)

# Fetch NBA Games for Today from a Public API
@st.cache_data
def get_nba_games():
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://www.balldontlie.io/api/v1/games?dates[]={today}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]:
            games = [f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}" for game in data['data']]
            return games
        else:
            return ["No games found for today"]
    return ["Error retrieving games"]

# Display NBA Games on the Left
st.sidebar.title("Today's NBA Games")
nba_games = get_nba_games()
st.sidebar.write("\n".join(nba_games))

# Placeholder Stats for Now
placeholder_stats = {
    "pts": 26.4, "reb": 7.1, "ast": 5.9, "minutes": 34.2, "usage_rate": 28.5, "pace": 100.4, "def_eff": 105.2
}

# Calculate Projections
def calculate_projections(stats):
    weight = {"minutes": 0.3, "usage_rate": 0.25, "pace": 0.15, "def_eff": 0.2, "recent": 0.1}
    proj_pts = (stats["minutes"] * weight["minutes"] +
                stats["usage_rate"] * weight["usage_rate"] +
                stats["pace"] * weight["pace"] -
                stats["def_eff"] * weight["def_eff"] +
                stats["pts"] * weight["recent"])
    proj_reb = stats["reb"] * 1.05
    proj_ast = stats["ast"] * 1.02
    return round(proj_pts, 1), round(proj_reb, 1), round(proj_ast, 1)

# Display Results
if player_name:
    proj_pts, proj_reb, proj_ast = calculate_projections(placeholder_stats)

    st.subheader(f"Projections for {player_name}")
    st.write(f"- Points: {proj_pts}")
    st.write(f"- Rebounds: {proj_reb}")
    st.write(f"- Assists: {proj_ast}")

    # Betting Recommendation
    st.subheader("Betting Recommendations:")
    st.write("✅ **Best Bets:**")
    if proj_pts > odds_pts:
        st.write(f"- Take **Over {odds_pts} Points**")
    else:
        st.write(f"- Take **Under {odds_pts} Points**")

    if proj_reb > odds_reb:
        st.write(f"- Take **Over {odds_reb} Rebounds**")
    else:
        st.write(f"- Take **Under {odds_reb} Rebounds**")

    if proj_ast > odds_ast:
        st.write(f"- Take **Over {odds_ast} Assists**")
    else:
        st.write(f"- Take **Under {odds_ast} Assists**")

    st.success("Use these insights for smarter bets!")
