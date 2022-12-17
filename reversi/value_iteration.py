from game import State, random_action
from settings import default_ratio_box
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import pickle
import os

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
        Path(f'./value_iteration_data/').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def reward(state: State, next_state: State):
    if not state.is_done():
        if next_state.is_done():
            if not state.is_first_player():
                return next_state.piece_count(next_state.enemy_pieces) - next_state.piece_count(next_state.pieces)
            else:
                return - (next_state.piece_count(next_state.enemy_pieces) - next_state.piece_count(next_state.pieces))
            # if next_state.is_lose():
            #     return 1
            # elif next_state.is_draw():
            #     return 0
            # else:
            #     return -1
        else:
            return 0
    else:
        return 0


cnt = -1

all_board = [None] * 63665
board_idx_dict = {}
state_d = {4: [], 5: [], 6: [], 7: [], 8: [], 9: [],
           10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: []}


def search(state: State):
    global all_board, board_idx_dict, cnt
    if not (tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2) in board_idx_dict:
        cnt += 1
        print(
            '\r{} {:,} / {:,}'.format(sys._getframe().f_code.co_name, cnt + 1, 63665), end='')
        board_idx_dict[(tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2)] = cnt
        all_board[cnt] = (state.pieces, state.enemy_pieces, state.depth % 2)

        piece_cnt = state.piece_count(state.pieces) + \
            state.piece_count(state.enemy_pieces)

        # 辞書に盤面の石の数ごとに登録
        if piece_cnt in state_d:
            tmp_l = state_d[piece_cnt]
            tmp_l.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
            state_d[piece_cnt] = tmp_l

        if not state.is_done():
            # 再帰処理で次のアクションに遷移
            for action in state.legal_actions():
                next_state = state.next(action=action)
                search(next_state)


def value_iter_onestep(V, first_player):
    global board_idx_dict, cnt
    # # 価値関数の設定
    cnt = 0
    for i in reversed(range(4, 16)):
        for state_idx in state_d[i]:
            print(
                '\r{} {:,} / {:,}'.format(sys._getframe().f_code.co_name, cnt + 1, 58613), end='')
            cnt += 1
            action_values = []
            pieces, enemy_pieces, depth = all_board[board_idx_dict[state_idx]]
            state = State(pieces, enemy_pieces,
                          default_ratio_box, depth % 2)
            if state.is_done():
                V[board_idx_dict[state_idx]] = 0
            else:
                # アクションごとの価値関数
                for action in state.legal_actions():
                    next_state = state.next(action)
                    na = board_idx_dict[(tuple(next_state.pieces), tuple(
                        next_state.enemy_pieces), next_state.depth % 2)]
                    r = reward(state, next_state)
                    v = r + (-1) * V[na]
                    action_values.append(v)
                if 4 <= i <= 9:
                    print(action_values)

                if state.is_first_player():
                    V[board_idx_dict[state_idx]] = min(action_values)
                else:
                    V[board_idx_dict[state_idx]] = max(action_values)
                # if first_player:
                # else:
                #     if state.is_first_player():
                #         V[board_idx_dict[state_idx]] = min(action_values)
                #     else:
                #         V[board_idx_dict[state_idx]] = max(action_values)

            del action_values, state
    print()
    return V


def value_iter(V, first_player, threshold=0.001):
    return value_iter_onestep(V, first_player)
    # while True:
    #     old_V = V.copy()
    #     V = value_iter_onestep(V)
    #     delta = 0
    #     for i in range(63665):
    #         t = abs(V[i] - old_V[i])
    #         if delta < t:
    #             delta = t
    #     if delta < threshold:
    #         break
    # return V


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def argmin(d: dict):
    """argmax 関数"""
    min_value = min(d.values())
    min_key = 0
    for key, value in d.items():
        if value == min_value:
            min_key = key
    return min_key


def greedy_policy(V, first_player):
    global all_board, board_idx_dict
    pi = [0] * 63665
    # # 価値関数の設定
    for i in range(63665):
        print(
            '\r{} {:,} / {:,}'.format(sys._getframe().f_code.co_name, i + 1, 63665), end='')
        pieces, enemy_pieces, depth = all_board[i]
        state = State(pieces, enemy_pieces,
                      default_ratio_box, depth % 2)
        len_tmp = len(state.legal_actions())
        action_probs = [0.0] * len_tmp

        # 終了している場合の方策はパス
        if state.is_done():
            action_probs = [1.0]
        else:
            action_values = {}
            for action in state.legal_actions():
                next_state = state.next(action)
                na = board_idx_dict[(tuple(next_state.pieces), tuple(
                    next_state.enemy_pieces), next_state.depth % 2)]
                r = reward(state, next_state)
                v = r + (-1) * V[na]
                action_values[action] = v

            if not state.is_first_player():
                max_action = argmax(action_values)

            else:
                max_action = argmin(action_values)

            # if first_player:
            #     max_action = argmax(action_values)
            # if state.is_first_player():
            #     max_action = argmax(action_values)
            # else:
            #     max_action = argmin(action_values)
            # else:
            #     max_action = argmax(action_values)
            # if state.is_first_player():
            #     max_action = argmin(action_values)
            # else:
            #     max_action = argmax(action_values)
            action_probs[state.legal_actions().index(max_action)] = 1.0
        pi[i] = action_probs
    print()
    return pi


def guess(V, first_player=True):
    V = value_iter(V, first_player)
    pi = greedy_policy(V, first_player)
    return V, pi


def play(V_1=None, pi_1=None, V_2=None, pi_2=None, n=100, bisible=False):
    for _ in range(1):
        black_win = 0
        white_win = 0
        for _ in range(n):
            state = State()
            # ゲーム終了までループ
            while True:
                # ゲーム終了時

                # 文字列表示
                if bisible:
                    print(V_2[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2)]])
                    print(state.legal_actions())
                    print(pi_2[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2)]])
                    print(state)

                if state.is_done():
                    if state.is_first_player():
                        if state.piece_count(state.pieces) > state.piece_count(state.enemy_pieces):
                            black_win += 1
                        elif state.piece_count(state.pieces) < state.piece_count(state.enemy_pieces):
                            white_win += 1
                    else:
                        if state.piece_count(state.pieces) > state.piece_count(state.enemy_pieces):
                            white_win += 1
                        elif state.piece_count(state.pieces) < state.piece_count(state.enemy_pieces):
                            black_win += 1
                    break

                # action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(tuple(state.pieces), tuple(
                #     state.enemy_pieces), state.depth % 2)]])
                # 行動の取得
                if not state.is_first_player():
                    action = np.random.choice(state.legal_actions(), p=pi_2[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2)]])
                else:
                    action = random_action(state)
                    # action = np.random.choice(state.legal_actions(), p=pi_1[board_idx_dict[(tuple(state.pieces), tuple(
                    #     state.enemy_pieces), state.depth % 2)]])

                # 次の状態の取得
                state = state.next(action)

        print(f"{black_win} : {white_win}")


# 動作確認
if __name__ == '__main__':
    state = State()
    search(state=state)
    print()
    del state
    # V = [0] * 63665
    # V_1, pi_1 = guess(V, first_player=True)
    V = [0] * 63665
    V_2, pi_2 = guess(V, first_player=False)
    # write_data([V_2, pi_2, board_idx_dict])
    # history = load_data()
    # V_2 = history[0]
    # pi_2 = history[1]
    # board_idx_dict = history[2]
    play(V_2=V_2, pi_2=pi_2, n=1000, bisible=False)
