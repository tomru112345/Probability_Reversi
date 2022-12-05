from game import State
# from cppState import State
from collections import defaultdict
from settings import default_ratio_box
from typing import List
from datetime import datetime
from pathlib import Path
import sys
import pickle
import gc
import itertools


# def load_data():
#     """学習データの読み込み"""
#     history_path = sorted(
#         Path(f'./policy_iteration_data/').glob('*.history'))[-1]
#     with history_path.open(mode='rb') as f:
#         return pickle.load(f)

# history = load_data()
# pi: dict = history[0]
# V: dict = history[1]
# del history
# gc.collect()

# n_0 = [-1, 0, 1]
# n_1 = [-1, 1]
# all_board = itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
#                               n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0)

# bool_l = [True, False]
# all_board_alpha = itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
#                                     n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0, bool_l)


def set_state(board, flg):
    board = list(board)
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


def init_pi_v():
    n_0 = [-1, 0, 1]
    n_1 = [-1, 1]
    bool_l = [True, False]
    all_board = list(itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                                       n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0, bool_l))
    del n_0, n_1, bool_l
    pi_value = [None] * 17006112
    V_value = [0.0] * 17006112
    cnt = 0
    for i in range(17006112):
        state = set_state(list(all_board[i][:16]), all_board[i][16:])
        tmp_l = [0.0] * 17
        legal_action_list = state.legal_actions()
        action_num = len(legal_action_list)
        for j in range(17):
            if j in legal_action_list:
                tmp_l[j] = 1.0 / float(action_num)
            else:
                tmp_l[j] = 0.0
        pi_value[i] = tmp_l
        del state, action_num, legal_action_list, tmp_l
        cnt += 1
        if cnt % 100000 == 0:
            gc.collect()
        print('\rinit_pi_v {} / {}'.format(cnt, 17006112), end='')
    print()
    pi = dict(zip(all_board, pi_value))
    V = dict(zip(all_board, V_value))
    del all_board, pi_value, V_value
    gc.collect()
    return pi, V

    # for board in all_board:
    #     state = set_state(list(board[:16]), board[16:])
    #     tmp_l = [0.0] * 17
    #     legal_action_list = state.legal_actions()
    #     action_num = len(legal_action_list)
    #     for i in range(17):
    #         if i in legal_action_list:
    #             tmp_l[i] = 1.0 / float(action_num)
    #         else:
    #             tmp_l[i] = 0.0
    #     pi[board] = tmp_l
    #     V[board] = 0
    #     del board, state, action_num, legal_action_list, tmp_l
    #     cnt += 1
    #     if cnt % 100000 == 0:
    #         gc.collect()
    #     print('\rinit_pi_v {} / {}'.format(cnt, 17006112), end='')
    # print()
    # del all_board
    # gc.collect()
    # return pi, V


# print(sys.getsizeof(all_board))
# print(sys.getsizeof(all_board_alpha))
# for board in all_board_alpha:
#     print(board[16:])
pi, V = init_pi_v()
print(sys.getsizeof(pi))
print(sys.getsizeof(V))
