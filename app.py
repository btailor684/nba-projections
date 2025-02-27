# Fetch Player Stats
def fetch_player_stats(player_id):
    url = f"https://api.balldontlie.io/v1/season_averages?season=2024&player_ids={player_id}"  # Corrected format

    # Debugging: Print the API request to verify correctness
    st.write(f"🔍 Debug: Player Stats API Request - [API Link]({url})")

    try:
        response = requests.get(url, headers=HEADERS)

        # Debug: Print API response
        st.write(f"🔍 Debug: API Response - {response.json()}")

        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                stats = data["data"][0]
                return {
                    "PTS": stats.get("pts", 0),
                    "AST": stats.get("ast", 0),
                    "REB": stats.get("reb", 0),
                    "FG%": round(stats.get("fg_pct", 0) * 100, 1) if stats.get("fg_pct") else 0
                }
        return None
    except Exception as e:
        return None
