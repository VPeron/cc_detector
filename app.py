import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO
import chess.pgn
from stockfish import Stockfish

# stockfish init
stockfish = Stockfish(
    '/home/vini/Personal/test_project/stockfish_14_linux_x64/stockfish_14_linux_x64/stockfish_14_x64', 
    parameters={"Threads": 2, 'Min Split Depth': 20, 'Ponder':True}
)
stockfish.set_elo_rating(2600)
stockfish.set_skill_level(30)


# HEADER
# st.write('# CHESS FILES') 
st.write('## Human vs Engine Detection')
img = "https://images3.alphacoders.com/235/235755.jpg"
st.image(img)

# DATA
@st.cache
def get_data():
    url_ep = 'http://127.0.0.1:8000/data'
    res = requests.get(url_ep)
    result = res.json()
    df_players = pd.DataFrame(result['players'])
    df_games = pd.DataFrame(result['games'])
    # df_moves = pd.DataFrame(result['moves'])
    return df_players, df_games #, df_moves

df_players, df_games = get_data()


# SIDEBAR
def sidebar():
    """
    sidebar dropdown player/games list
    """
    # title
    st.sidebar.write('## Local Viewbar')
    st.sidebar.write('### Computer vs player files')
    # dropdown
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
        st.write('### Local Games')
        st.write(df_games)
        
sidebar()


def sidebar_player_search():
    """ 
    Local DB Player search with ranking progression graph
    """
    input_name = st.sidebar.text_input('Search Local DB Player Names', '')
    if input_name:
        white = df_games[df_games['White'] == input_name]
        black = df_games[df_games['Black'] == input_name]
        player = white.append(black)
        if len(player) > 0:
            st.sidebar.write('Mainscreen View')
            st.write(f"### {input_name}'s games")
            st.write(player)
            
            if len(white) > 2 and len(black) > 2:
                # PLOT
                fig, ax = plt.subplots(figsize=(18,8))
                # player['Date'] = pd.to_datetime(player['Date'])
                # player.sort_values(by='Date', inplace=True)
                plt.subplot(1,2,1)
                plt.title('as White')
                plt.plot(white['White_Elo'])
                plt.grid()
                plt.subplot(1,2,2)
                plt.title('as Black')
                plt.plot(black['Black_Elo'])
                plt.grid()
                st.pyplot(fig)
        else:
            st.sidebar.write(f'Player name "{input_name}" not found.')
            
sidebar_player_search()


# st.write('## Human vs Human?')
# UPLOAD PGN FILE
def upload_pgn():
    """
    PGN needs StringIO to be read so file can be read as a string. chess lybrary loses strength here, hence stockfish.
    """
    st.write('# Load Your PGN')

    uploaded_file = st.file_uploader("Feed the engine.")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # CHESS.PGN
        game = chess.pgn.read_game(stringio)
        board = game.board()
        moves = list(game.mainline_moves())
        variations = game.mainline()  # variation.comment no longer exists - REGEX vs Stockfish ?
        
        evals = []
        for move in moves:
            board.push(move)
            fen = board.fen()
            stockfish.set_fen_position(fen)
            eval = stockfish.get_evaluation()
            evals.append(float(eval['value']))
        
        # PLOT GAME EVALS
        st.write('Powered by Stockfish 14')
        fig, ax = plt.subplots()
        plt.title(f"{game.headers['White']} vs {game.headers['Black']}")
        plt.plot(evals)
        zeros = np.zeros(len(evals))
        plt.plot(zeros)
        plt.ylabel('CP Advantage')
        plt.xlabel('Moves')
        plt.grid()
        st.pyplot(fig)
        
upload_pgn()
