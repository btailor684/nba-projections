import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ✅ Keep API Key in Memory - Ensure this remains set at all times
API_KEY = "d8b9eafb-926c-4a16-9ca3-3743e5aee7e8"
HEADERS = {"Authorization": API_KEY}
BASE_URL = "https://api.balldontlie.io/v1"

# ✅ Function to Fetch Today's NBA Games
def fetch_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/games?dates[]={today}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    
    st.error(f"❌ Error Fetching Games: {response.status_code} - {response.text}")
    return []

# ✅ Function to Fetch Active Players for a Selected Game
def fetch_active_players(team_id):
    url = f"{BASE_URL}/players/active?team_ids[]={team_id}&per_page=100"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    
    st.error(f"❌ Error Fetching Players: {response.status_code} - {response.text}")
    return []

# ✅ Function to Fetch Player Season Averages
def fetch_player_season_averages(player_id):
    url = f"{BASE_URL}/season_averages?season=2024&player_id={player_id}"  # ✅ FIXED PLAYER ID FORMAT
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json().get("data", [])

        if data:
            return {
                "Points Per Game": f"**{data[0].get('pts', 'N/A')}**",
                "Rebounds Per Game": f"**{data[0].get('reb', 'N/A')}**",
                "Assists Per Game": f"**{data[0].get('ast', 'N/A')}**",
                "Field Goal %": f"**{round(data[0].get('fg_pct', 0) * 100, 1)}%**" if data[0].get('fg_pct') else "**N/A**",
                "Minutes Per Game": f"**{data[0].get('min', 'N/A')}**",
            }
        else:
            st.warning("⚠️ No season averages available for this player.")
    
    st.error(f"❌ API Error: {response.status_code} - {response.text}")  # ✅ ERROR LOGGING
    return None

# ✅ Streamlit UI Setup
st.sidebar.title("🏀 Today's NBA Games")
st.sidebar.write("View today's NBA games and players.")

games = fetch_games()
game_options = {f"{game['home_team']['full_name']} vs {game['visitor_team']['full_name']}": game for game in games}
selected_game = st.sidebar.selectbox("Select a Game", list(game_options.keys()))

if selected_game:
    game_data = game_options[selected_game]
    home_team = game_data["home_team"]
    away_team = game_data["visitor_team"]
    game_time = datetime.strptime(game_data["date"], "%Y-%m-%d").strftime("%B %d, %Y - 7:00 PM ET")

    st.title("🏀 PropEdge NBA")
    st.write("View today's NBA games and players.")
    st.header(f"Players for {home_team['full_name']} vs {away_team['full_name']}")
    st.markdown(f"### 🕒 Game Time: **{game_time}**")

    # ✅ Fetching Players for Both Teams
    players_home = fetch_active_players(home_team["id"])
    players_away = fetch_active_players(away_team["id"])
    players = players_home + players_away

    if players:
        player_dict = {f"{player['first_name']} {player['last_name']}": player["id"] for player in players}
        selected_player = st.selectbox("Select a Player", list(player_dict.keys()))

        if selected_player:
            player_id = player_dict[selected_player]
            st.write(f"📊 Fetching stats for: **{selected_player} (ID: {player_id})**")

            # ✅ Fetch and Display Season Averages
            season_avg = fetch_player_season_averages(player_id)
            if season_avg:
                st.subheader(f"📊 **Season Averages for {selected_player}**")
                season_df = pd.DataFrame([season_avg])
                
                # ✅ Improve Readability with Larger Font
                st.markdown(
                    f"""
                    <style>
                    .dataframe th, .dataframe td {{
                        font-size: 18px !important;
                        text-align: center;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                st.table(season_df)
            else:
                st.warning("⚠️ No season averages available for this player.")

    else:
        st.warning("⚠️ No active players found for this game.")

st.write("Built with ❤️ for NBA fans | Data: balldontlie.io")
