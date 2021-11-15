import streamlit as st
import pandas as pd
import numpy as np
from cc_detector.data import ChessData
import matplotlib.pyplot as plt
import requests


# HEADER
st.write('# Chess Files')
st.write('## Chap 1 - Human vs Engine Detection')
img = "https://images3.alphacoders.com/235/235755.jpg"
st.image(img)

# DATA
@st.cache
def get_data():
    url_ep = 'http://127.0.0.1:8000/predict'
    res = requests.get(url_ep)
    result = res.json()
    df_players = pd.DataFrame(result['players'])
    df_games = pd.DataFrame(result['games'])
    # df_moves = pd.DataFrame(result['moves'])
    return df_players, df_games #, df_moves

df_players, df_games = get_data()

# st.write(df_players)
# st.write(df_games)

# Player search with ranking graph
def player_search():
    title = st.text_input('Search Player games', '')
    if title:
        white = df_games[df_games['White'] == title]
        black = df_games[df_games['Black'] == title]
        player = white.append(black)
        st.write(player)
        
        if len(player) > 1:
            # PLOT
            fig, ax = plt.subplots()
            player['Date'] = pd.to_datetime(player['Date'])
            player.sort_values(by='Date', inplace=True)
            plt.title('Rating')
            plt.plot(player['White_Elo'])
            plt.grid()
            st.pyplot(fig)
            
player_search()

# SIDEBAR
def sidebar():
    # title
    st.sidebar.write('## Files sidebar')
    # 1st dropdown
    add_selectbox = st.sidebar.selectbox(
        "Select list view.",
        ("players", "games")
    )
    if add_selectbox == 'players':
        white = df_players['White'].unique()
        black = df_players['Black'].unique()
        players = np.concatenate((white, black))
        st.sidebar.write(players)
        
    if add_selectbox == 'games':
        st.sidebar.write('See Mainscreen View')
        st.write(df_games)
        
sidebar()



