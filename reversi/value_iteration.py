from game import State
# from cppState import State
from settings import default_ratio_box
from datetime import datetime
from pathlib import Path
import sys
import pickle
import os
import itertools
import gc

sys.setrecursionlimit(10 ** 9)


def write_data(history):
    """学習データの保存"""
    now = datetime.now()
    os.makedirs(f'./value_iteration_data/', exist_ok=True)  # フォルダがない時は生成
    path = './value_iteration_data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    with open(path, mode='wb') as f:
        pickle.dump(history, f)


def load_data():
    """学習データの読み込み"""
    history_path = sorted(
        Path(f'./policy_iteration_data/').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def set_state(board):
    flg = board[16:]
    board = list(board[:16])
    pieces = [0] * 16
    enemy_pieces = [0] * 16
    for i in range(16):
        if board[i] == 1:
            pieces[i] = 1
        elif board[i] == -1:
            enemy_pieces[i] = 1
    if flg:
        state = State(pieces, enemy_pieces, default_ratio_box, 0)
    else:
        state = State(pieces, enemy_pieces, default_ratio_box, 1)
    return state


def set_board(state):
    board = [0] * 17
    for i in range(16):
        if state.pieces[i] == 1:
            board[i] = 1
        elif state.enemy_pieces[i] == 1:
            board[i] = -1
    if state.is_first_player():
        board[16] = True
    else:
        board[16] = False
    board = tuple(board)
    return board


def first_player_value(state: State, next_state: State):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if not state.is_lose():
        if next_state.is_lose():
            return -1.0 if next_state.is_first_player() else 1.0
    return 0.0


def init():
    n_0 = [-1, 0, 1]
    n_1 = [-1, 1]
    bool_flg_l = [True, False]
    all_board = itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                                  n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0, bool_flg_l)
    del n_0, n_1, bool_flg_l
    cnt = 0
    adress_4 = []
    adress_5 = []
    adress_6 = []
    adress_7 = []
    adress_8 = []
    adress_9 = []
    adress_10 = []
    adress_11 = []
    adress_12 = []
    adress_13 = []
    adress_14 = []
    adress_15 = []
    adress_16 = []
    for board in all_board:
        print('\reval_onestep {:,} / {:,}'.format(cnt, 17006112), end='')
        state = set_state(board)
        piece_cnt = state.piece_count(state.pieces) + \
            state.piece_count(state.enemy_pieces)
        if piece_cnt == 4:
            adress_4.append(cnt)
        if piece_cnt == 5:
            adress_5.append(cnt)
        if piece_cnt == 6:
            adress_6.append(cnt)
        if piece_cnt == 7:
            adress_7.append(cnt)
        if piece_cnt == 8:
            adress_8.append(cnt)
        if piece_cnt == 9:
            adress_9.append(cnt)
        if piece_cnt == 10:
            adress_10.append(cnt)
        if piece_cnt == 11:
            adress_11.append(cnt)
        if piece_cnt == 12:
            adress_12.append(cnt)
        if piece_cnt == 13:
            adress_13.append(cnt)
        if piece_cnt == 14:
            adress_14.append(cnt)
        if piece_cnt == 15:
            adress_15.append(cnt)
        if piece_cnt == 16:
            adress_16.append(cnt)
        del state, board, piece_cnt
        # del action_num, legal_action_list, tmp_l
        if cnt % 100000 == 0:
            gc.collect()
        cnt += 1
    print()
    print(len(adress_16))
    print(len(adress_15))
    print(len(adress_14))
    address = [
        adress_16,
        adress_15,
        adress_14,
        adress_13,
        adress_12,
        adress_11,
        adress_10,
        adress_9,
        adress_8,
        adress_7,
        adress_6,
        adress_5,
        adress_4,
    ]
    return address


def value_iter_onestep(address: list):
    n_0 = [-1, 0, 1]
    n_1 = [-1, 1]
    bool_flg_l = [True, False]
    all_board = list(itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                                       n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0, bool_flg_l))
    del n_0, n_1, bool_flg_l
    cnt = 0
    V = {}
    for i in range(13):
        for a in address[i]:
            print(
                '\rvalue_iter_onestep {:,} / {:,}'.format(cnt, 17006112), end='')
            if i == 0:
                V[a] = 0
            elif i == 1:
                state = set_state(all_board[a])
                if (state.piece_count(state.pieces) == 0) or (state.piece_count(state.enemy_pieces) == 0):
                    V[a] = 0
                elif state.is_done():
                    V[a] = 0
                else:
                    action_values = []
                    for action in state.legal_actions():
                        next_state = state.next(action)
                        v = first_player_value(state, next_state)
                        action_values.append(v)
                    V[a] = max(action_values)
                    del next_state, action_values
                del state
            else:
                state = set_state(all_board[a])
                if (state.piece_count(state.pieces) == 0) or (state.piece_count(state.enemy_pieces) == 0):
                    V[a] = 0
                elif state.is_done():
                    V[a] = 0
                else:
                    action_values = []
                    for action in state.legal_actions():
                        next_state = state.next(action)
                        next_board = set_board(next_state)
                        na = all_board.index(next_board)
                        if na == 17006067:
                            print(all_board[a])
                            print(next_board)
                        if action == 16 and next_state.legal_actions() == [16]:
                            V[na] = 0
                        elif action == 16:
                            next_action_values = []
                            for next_action in next_state.legal_actions():
                                nnext_state = next_state.next(next_action)
                                nnext_board = set_board(nnext_state)
                                nna = all_board.index(nnext_board)
                                nr = first_player_value(
                                    next_state, nnext_state)
                                nv = nr + V[nna]
                                next_action_values.append(nv)
                            V[na] = max(next_action_values)
                            del next_action_values
                        r = first_player_value(state, next_state)
                        v = r + V[na]
                        action_values.append(v)
                    V[a] = max(action_values)
                    del next_state, action_values
                del state
            cnt += 1
    return V


def main():
    address = init()
    # write_data([address])
    # history = load_data()
    # address = history[0]
    print(sys.getsizeof(address))
    V = value_iter_onestep(address=address)
    # print(sys.getsizeof(V))

    # 動作確認
if __name__ == '__main__':
    main()
