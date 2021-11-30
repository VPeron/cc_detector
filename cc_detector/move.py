import chess
import pandas as pd
import numpy as np


#functions for the data import and parsing
def set_move_dict():
    move_dict = {
        'Game_ID': [],
        'FEN_moves': [],
        'Bitmap_moves': [],
        'WhiteIsComp': [],
        'turn': [],
        'Castling_right': [],
        'EP_option': [],
        'Pseudo_EP_option': [],
        'Halfmove_clock': [],
        'Evaluation': []
        }
    return move_dict

def move_info_extractor(game, board, move_dict):
    move_dict['Game_ID'].append(game.headers['FICSGamesDBGameNo'])
    move_dict['FEN_moves'].append(board.fen())
    return move_dict

def bitmap_representer(board, pieces, squares, move_dict):
    bitmap_board_dict = {}
    positions = board.piece_map()

    for piece in pieces:
        bitmap_board = {}
        for square in squares:
            if square in positions.keys():
                if positions[square] == piece:
                    bitmap_board[square] = 1
                else:
                    bitmap_board[square] = 0
            else:
                bitmap_board[square] = 0
        bitmap_board_dict[str(piece)] = bitmap_board

    move_dict['Bitmap_moves'].append(bitmap_board_dict)
    return move_dict

def castling_right(game, board, move_dict, white):
    if ("BlackIsComp" in game.headers.keys()) or\
        ("WhiteIsComp" in game.headers.keys()):
        move_dict['WhiteIsComp'].append(game.headers.get('WhiteIsComp', 'No'))
    else:
        move_dict['WhiteIsComp'].append("NA")

    if white:
        move_dict['turn'].append('white')
        move_dict['Castling_right'].append(
            int(board.has_castling_rights(chess.WHITE)))
        white = False
    else:
        move_dict['turn'].append('black')
        move_dict['Castling_right'].append(
            int(board.has_castling_rights(chess.BLACK)))
        white = True

    return move_dict, white

def en_passant_opp(board, move_dict):
    move_dict['EP_option'].append(int(board.has_legal_en_passant()))
    move_dict['Pseudo_EP_option'].append(
        int(board.has_pseudo_legal_en_passant()))
    return move_dict

def halfmove_clock(board, move_dict):
    """Counts half-moves goneby without a capture or pawn move."""
    move_dict['Halfmove_clock'].append(board.halfmove_clock)
    return move_dict

# def move_dict_maker(game, board, move_dict, white, pieces):
#     move_dict = move_info_extractor(game, board, move_dict)
#     move_dict = bitmap_representer(board, pieces, move_dict)
#     move_dict, white = castling_right(game, board, move_dict, white)
#     move_dict = en_passant_opp(board, move_dict)
#     move_dict = halfmove_clock(board, move_dict)
#     return move_dict, white


## Functions that work with the dataframe generated from the data import

def binary_board_df(move_df):
    df_header = pd.DataFrame(move_df['Bitmap_moves'][0])
    headers = []
    for i in df_header.columns:
        for j in df_header.index:
            headers.append(str(i) + str(j))

    boards = []
    for line in range(len(move_df['Bitmap_moves'])):
        df_board = pd.DataFrame(move_df['Bitmap_moves'][line]).to_numpy()
        array_wide = df_board.flatten('F')
        boards.append(array_wide.reshape(1, -1))

    df_wide = pd.DataFrame(np.concatenate(boards), columns=headers)

    return df_wide

def binary_board_headers(move_df):
    df_header = pd.DataFrame(move_df['Bitmap_moves'][0])
    headers = []
    for i in df_header.columns:
        for j in df_header.index:
            headers.append(str(i) + str(j))

    return headers

def get_bitmap_header():
    bitmap_headers = [
        'P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10',
        'P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'P17', 'P18', 'P19', 'P20',
        'P21', 'P22', 'P23', 'P24', 'P25', 'P26', 'P27', 'P28', 'P29', 'P30',
        'P31', 'P32', 'P33', 'P34', 'P35', 'P36', 'P37', 'P38', 'P39', 'P40',
        'P41', 'P42', 'P43', 'P44', 'P45', 'P46', 'P47', 'P48', 'P49', 'P50',
        'P51', 'P52', 'P53', 'P54', 'P55', 'P56', 'P57', 'P58', 'P59', 'P60',
        'P61', 'P62', 'P63', 'N0', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7',
        'N8', 'N9', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15', 'N16', 'N17',
        'N18', 'N19', 'N20', 'N21', 'N22', 'N23', 'N24', 'N25', 'N26', 'N27',
        'N28', 'N29', 'N30', 'N31', 'N32', 'N33', 'N34', 'N35', 'N36', 'N37',
        'N38', 'N39', 'N40', 'N41', 'N42', 'N43', 'N44', 'N45', 'N46', 'N47',
        'N48', 'N49', 'N50', 'N51', 'N52', 'N53', 'N54', 'N55', 'N56', 'N57',
        'N58', 'N59', 'N60', 'N61', 'N62', 'N63', 'B0', 'B1', 'B2', 'B3', 'B4',
        'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15',
        'B16', 'B17', 'B18', 'B19', 'B20', 'B21', 'B22', 'B23', 'B24', 'B25',
        'B26', 'B27', 'B28', 'B29', 'B30', 'B31', 'B32', 'B33', 'B34', 'B35',
        'B36', 'B37', 'B38', 'B39', 'B40', 'B41', 'B42', 'B43', 'B44', 'B45',
        'B46', 'B47', 'B48', 'B49', 'B50', 'B51', 'B52', 'B53', 'B54', 'B55',
        'B56', 'B57', 'B58', 'B59', 'B60', 'B61', 'B62', 'B63', 'R0', 'R1',
        'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12',
        'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21', 'R22',
        'R23', 'R24', 'R25', 'R26', 'R27', 'R28', 'R29', 'R30', 'R31', 'R32',
        'R33', 'R34', 'R35', 'R36', 'R37', 'R38', 'R39', 'R40', 'R41', 'R42',
        'R43', 'R44', 'R45', 'R46', 'R47', 'R48', 'R49', 'R50', 'R51', 'R52',
        'R53', 'R54', 'R55', 'R56', 'R57', 'R58', 'R59', 'R60', 'R61', 'R62',
        'R63', 'Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9',
        'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18', 'Q19',
        'Q20', 'Q21', 'Q22', 'Q23', 'Q24', 'Q25', 'Q26', 'Q27', 'Q28', 'Q29',
        'Q30', 'Q31', 'Q32', 'Q33', 'Q34', 'Q35', 'Q36', 'Q37', 'Q38', 'Q39',
        'Q40', 'Q41', 'Q42', 'Q43', 'Q44', 'Q45', 'Q46', 'Q47', 'Q48', 'Q49',
        'Q50', 'Q51', 'Q52', 'Q53', 'Q54', 'Q55', 'Q56', 'Q57', 'Q58', 'Q59',
        'Q60', 'Q61', 'Q62', 'Q63', 'K0', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6',
        'K7', 'K8', 'K9', 'K10', 'K11', 'K12', 'K13', 'K14', 'K15', 'K16',
        'K17', 'K18', 'K19', 'K20', 'K21', 'K22', 'K23', 'K24', 'K25', 'K26',
        'K27', 'K28', 'K29', 'K30', 'K31', 'K32', 'K33', 'K34', 'K35', 'K36',
        'K37', 'K38', 'K39', 'K40', 'K41', 'K42', 'K43', 'K44', 'K45', 'K46',
        'K47', 'K48', 'K49', 'K50', 'K51', 'K52', 'K53', 'K54', 'K55', 'K56',
        'K57', 'K58', 'K59', 'K60', 'K61', 'K62', 'K63', 'p0', 'p1', 'p2',
        'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13',
        'p14', 'p15', 'p16', 'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23',
        'p24', 'p25', 'p26', 'p27', 'p28', 'p29', 'p30', 'p31', 'p32', 'p33',
        'p34', 'p35', 'p36', 'p37', 'p38', 'p39', 'p40', 'p41', 'p42', 'p43',
        'p44', 'p45', 'p46', 'p47', 'p48', 'p49', 'p50', 'p51', 'p52', 'p53',
        'p54', 'p55', 'p56', 'p57', 'p58', 'p59', 'p60', 'p61', 'p62', 'p63',
        'n0', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9', 'n10',
        'n11', 'n12', 'n13', 'n14', 'n15', 'n16', 'n17', 'n18', 'n19', 'n20',
        'n21', 'n22', 'n23', 'n24', 'n25', 'n26', 'n27', 'n28', 'n29', 'n30',
        'n31', 'n32', 'n33', 'n34', 'n35', 'n36', 'n37', 'n38', 'n39', 'n40',
        'n41', 'n42', 'n43', 'n44', 'n45', 'n46', 'n47', 'n48', 'n49', 'n50',
        'n51', 'n52', 'n53', 'n54', 'n55', 'n56', 'n57', 'n58', 'n59', 'n60',
        'n61', 'n62', 'n63', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7',
        'b8', 'b9', 'b10', 'b11', 'b12', 'b13', 'b14', 'b15', 'b16', 'b17',
        'b18', 'b19', 'b20', 'b21', 'b22', 'b23', 'b24', 'b25', 'b26', 'b27',
        'b28', 'b29', 'b30', 'b31', 'b32', 'b33', 'b34', 'b35', 'b36', 'b37',
        'b38', 'b39', 'b40', 'b41', 'b42', 'b43', 'b44', 'b45', 'b46', 'b47',
        'b48', 'b49', 'b50', 'b51', 'b52', 'b53', 'b54', 'b55', 'b56', 'b57',
        'b58', 'b59', 'b60', 'b61', 'b62', 'b63', 'r0', 'r1', 'r2', 'r3', 'r4',
        'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15',
        'r16', 'r17', 'r18', 'r19', 'r20', 'r21', 'r22', 'r23', 'r24', 'r25',
        'r26', 'r27', 'r28', 'r29', 'r30', 'r31', 'r32', 'r33', 'r34', 'r35',
        'r36', 'r37', 'r38', 'r39', 'r40', 'r41', 'r42', 'r43', 'r44', 'r45',
        'r46', 'r47', 'r48', 'r49', 'r50', 'r51', 'r52', 'r53', 'r54', 'r55',
        'r56', 'r57', 'r58', 'r59', 'r60', 'r61', 'r62', 'r63', 'q0', 'q1',
        'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12',
        'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22',
        'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q29', 'q30', 'q31', 'q32',
        'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39', 'q40', 'q41', 'q42',
        'q43', 'q44', 'q45', 'q46', 'q47', 'q48', 'q49', 'q50', 'q51', 'q52',
        'q53', 'q54', 'q55', 'q56', 'q57', 'q58', 'q59', 'q60', 'q61', 'q62',
        'q63', 'k0', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'k8', 'k9',
        'k10', 'k11', 'k12', 'k13', 'k14', 'k15', 'k16', 'k17', 'k18', 'k19',
        'k20', 'k21', 'k22', 'k23', 'k24', 'k25', 'k26', 'k27', 'k28', 'k29',
        'k30', 'k31', 'k32', 'k33', 'k34', 'k35', 'k36', 'k37', 'k38', 'k39',
        'k40', 'k41', 'k42', 'k43', 'k44', 'k45', 'k46', 'k47', 'k48', 'k49',
        'k50', 'k51', 'k52', 'k53', 'k54', 'k55', 'k56', 'k57', 'k58', 'k59',
        'k60', 'k61', 'k62', 'k63'
    ]
    return bitmap_headers
