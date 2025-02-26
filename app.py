import streamlit as st

# Title
st.title("NBA Player Projection & Betting Tool")

# Static List of NBA Players (No API Calls)
nba_players = [
    "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo", "Luka Doncic", "Nikola Jokic",
    "Jayson Tatum", "Joel Embiid", "Devin Booker", "Damian Lillard", "Anthony Davis", "Jimmy Butler"
]

# User Input - Player Name with Autocomplete
player_name = st.selectbox("Enter NBA Player Name", nba_players, index=0)

# User Input - Sportsbook Odds
st.subheader("Enter Sportsbook Over/Under Lines:")
odds_pts = st.number_input("Over/Under Points", value=25.5)
odds_reb = st.number_input("Over/Under Rebounds", value=6.5)
odds_ast = st.number_input("Over/Under Assists", value=5.5)

# Fetch Mock NBA Stats
def get_player_stats(player_name):
    return {
        "pts": 26.4,
        "reb": 7.1,
        "ast": 5.9,
        "minutes": 34.2,
        "usage_rate": 28.5,
        "pace": 100.4,
        "def_eff": 105.2  # Opponent Defensive Efficiency
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
    stats = get_player_stats(player_name)
    proj_pts, proj_reb, proj_ast = calculate_projections(stats)

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
