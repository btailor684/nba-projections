import streamlit as st

st.title("NBA Player Projections")
st.write("Enter a player's name to get projected stats.")

player_name = st.text_input("Player Name")
if player_name:
    st.write(f"Projections for {player_name}:")
    st.write("- Points: 25.4")
    st.write("- Rebounds: 6.7")
    st.write("- Assists: 5.2")
