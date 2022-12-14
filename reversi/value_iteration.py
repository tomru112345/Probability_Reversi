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
            if next_state.is_lose():
                return 1
            elif next_state.is_draw():
                return 0
            else:
                return -1
        else:
            return 0
    else:
        return 0


cnt = -1

all_board = [None] * 63665
board_idx_dict = {}
state_d = {4: [], 5: [], 6: [], 7: [], 8: [], 9: [],
           10: [], 11: [], 12: [], 13: [], 14: [], 15: []}


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


def value_iter_onestep(V, gamma):
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
            # アクションごとの価値関数
            for action in state.legal_actions():
                next_state = state.next(action)
                na = board_idx_dict[(tuple(next_state.pieces), tuple(
                    next_state.enemy_pieces), next_state.depth % 2)]
                r = reward(state, next_state)
                v = r + (-1) * gamma * V[na]
                action_values.append(v)
            V[board_idx_dict[state_idx]] = max(action_values)
            del action_values, state
    print()
    return V


def value_iter(V, gamma, threshold=0.001):
    # return value_iter_onestep(V, gamma)
    while True:
        old_V = V.copy()
        V = value_iter_onestep(V, gamma)
        delta = 0
        for i in range(63665):
            t = abs(V[i] - old_V[i])
            if delta < t:
                delta = t
        if delta < threshold:
            break
    return V


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def greedy_policy(V, gamma):
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
                v = r + (-1) * gamma * V[na]
                action_values[action] = v
            max_action = argmax(action_values)
            action_probs[state.legal_actions().index(max_action)] = 1.0
        pi[i] = action_probs
    print()
    return pi


def guess(gamma):
    V = [0] * 63665
    state = State()
    search(state=state)
    print()
    del state
    V = value_iter(V, gamma)
    pi = greedy_policy(V, gamma)
    return V, pi


def play(V, pi, n):
    for _ in range(100):
        black_win = 0
        white_win = 0
        for _ in range(n):
            state = State()
            # ゲーム終了までループ
            while True:
                # ゲーム終了時

                # 文字列表示
                # print(V[board_idx_dict[(tuple(state.pieces), tuple(
                #         state.enemy_pieces), state.depth % 2)]])
                # print(state.legal_actions())
                # print(pi[board_idx_dict[(tuple(state.pieces), tuple(
                #     state.enemy_pieces), state.depth % 2)]])
                # print(state)

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
                    action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2)]])
                else:
                    action = random_action(state)

                # 次の状態の取得
                state = state.next(action)

        print(f"{black_win} : {white_win}")


# 動作確認
if __name__ == '__main__':
    # V, pi = guess(gamma=0.5)
    # write_data([V, pi, board_idx_dict])
    history = load_data()
    V = history[0]
    pi = history[1]
    board_idx_dict = history[2]
    play(V, pi, 100)
