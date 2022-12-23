from game import State, random_action
from settings import default_ratio_box, p
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
            # if not state.is_first_player():
            #     return (next_state.piece_count(next_state.enemy_pieces) - next_state.piece_count(next_state.pieces))
            # else:
            #     return -1 * (next_state.piece_count(next_state.enemy_pieces) - next_state.piece_count(next_state.pieces))

            if not state.is_first_player():
                if next_state.is_lose():
                    return 1
                elif next_state.is_draw():
                    return 0
                else:
                    return -1
            else:
                if next_state.is_lose():
                    return -1
                elif next_state.is_draw():
                    return 0
                else:
                    return 1
        else:
            return 0
    else:
        return 0


cnt = -1

all_board = []
board_idx_dict = {}
state_d = {4: [], 5: [], 6: [], 7: [], 8: [], 9: [],
           10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: []}


def search(state: State):
    global all_board, board_idx_dict, cnt
    if not (tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2, state.pass_end) in board_idx_dict:
        cnt += 1
        print(
            '\r{} {:,}'.format(sys._getframe().f_code.co_name, cnt + 1), end='')
        board_idx_dict[(tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2, state.pass_end)] = cnt
        all_board.append((state.pieces, state.enemy_pieces,
                         state.depth % 2, state.pass_end))

        piece_cnt = state.piece_count(state.pieces) + \
            state.piece_count(state.enemy_pieces)

        # 辞書に盤面の石の数ごとに登録
        if piece_cnt in state_d:
            tmp_l = state_d[piece_cnt]
            tmp_l.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2, state.pass_end))
            state_d[piece_cnt] = tmp_l

        if not state.is_done():
            # 再帰処理で次のアクションに遷移
            for action in state.legal_actions():
                next_success_state = state.next(action=action, set_ratio=0)
                search(next_success_state)
                if p != 0:
                    next_failure_state = state.next(action=action, set_ratio=1)
                    search(next_failure_state)


def value_iter_onestep():
    global all_board, board_idx_dict, cnt
    # # 価値関数の設定

    V = [0] * len(all_board)
    cnt = 0
    for i in reversed(range(4, 16)):
        for state_idx in state_d[i]:
            print(
                '\r{} {:,}'.format(sys._getframe().f_code.co_name, cnt + 1), end='')
            cnt += 1
            action_values = []
            pieces, enemy_pieces, depth, pass_end = all_board[board_idx_dict[state_idx]]
            state = State(pieces, enemy_pieces,
                          default_ratio_box, depth % 2)
            state.pass_end = pass_end
            if state.is_done():
                V[board_idx_dict[state_idx]] = 0
            else:
                # アクションごとの価値関数
                for action in state.legal_actions():
                    next_success_state = state.next(action=action, set_ratio=0)
                    success_na = board_idx_dict[(tuple(next_success_state.pieces), tuple(
                        next_success_state.enemy_pieces), next_success_state.depth % 2, next_success_state.pass_end)]

                    if next_success_state.legal_actions() == [16] and not next_success_state.is_done():
                        pass_next_state = next_success_state.next(
                            action=16, set_ratio=0)
                        pass_na = board_idx_dict[(tuple(pass_next_state.pieces), tuple(
                            pass_next_state.enemy_pieces), pass_next_state.depth % 2, pass_next_state.pass_end)]
                        r = reward(next_success_state, pass_next_state)
                        V[success_na] = r + V[pass_na]

                    success_r = reward(state, next_success_state)
                    success_v = success_r + V[success_na]

                    if p != 0:
                        next_failure_state = state.next(
                            action=action, set_ratio=1)
                        failure_na = board_idx_dict[(tuple(next_failure_state.pieces), tuple(
                            next_failure_state.enemy_pieces), next_failure_state.depth % 2, next_failure_state.pass_end)]

                        if next_failure_state.legal_actions() == [16] and not next_failure_state.is_done():
                            pass_next_state = next_failure_state.next(
                                action=16, set_ratio=0)
                            pass_na = board_idx_dict[(tuple(pass_next_state.pieces), tuple(
                                pass_next_state.enemy_pieces), pass_next_state.depth % 2, pass_next_state.pass_end)]
                            r = reward(next_failure_state, pass_next_state)
                            V[failure_na] = r + V[pass_na]

                        failure_r = reward(state, next_failure_state)
                        failure_v = failure_r + V[failure_na]

                    else:
                        failure_v = 0

                    if action != 16:
                        v = (default_ratio_box[action] / 100) * success_v + \
                            (1 - default_ratio_box[action] / 100) * failure_v
                    else:
                        v = success_v
                    action_values.append(v)

                if state.is_first_player():
                    V[board_idx_dict[state_idx]] = min(action_values)
                else:
                    V[board_idx_dict[state_idx]] = max(action_values)

            del action_values, state
    print()
    return V


def value_iter():
    return value_iter_onestep()


def equal_all(d: dict):
    value_l = list(d.values())
    return all(val == value_l[0] for val in value_l)


def equal_max(d: dict):
    value_l = list(d.values())
    return value_l.count(max(d.values()))


def equal_min(d: dict):
    value_l = list(d.values())
    return value_l.count(min(d.values()))


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def set_argmax(d: dict, action_probs: list, state: State):
    """argmax 関数"""
    max_value = max(d.values())
    value_l = list(d.values())
    n = value_l.count(max_value)
    for key, value in d.items():
        if value == max_value:
            action_probs[state.legal_actions().index(key)] = 1 / n
    return action_probs


def argmin(d: dict):
    """argmin 関数"""
    min_value = min(d.values())
    min_key = 0
    for key, value in d.items():
        if value == min_value:
            min_key = key
    return min_key


def set_argmin(d: dict, action_probs: list, state: State):
    """argmax 関数"""
    min_value = min(d.values())
    value_l = list(d.values())
    n = value_l.count(min_value)
    for key, value in d.items():
        if value == min_value:
            action_probs[state.legal_actions().index(key)] = 1 / n
    return action_probs


def greedy_policy(V):
    global all_board, board_idx_dict
    pi = [0] * len(all_board)
    cnt = 0
    # 価値関数の設定
    for i in range(4, 17):
        for state_idx in state_d[i]:
            print(
                '\r{} {:,}'.format(sys._getframe().f_code.co_name, cnt + 1), end='')
            action_values = []
            pieces, enemy_pieces, depth, pass_end = all_board[board_idx_dict[state_idx]]
            state = State(pieces, enemy_pieces,
                          default_ratio_box, depth % 2)
            state.pass_end = pass_end
            len_tmp = len(state.legal_actions())
            action_probs = [0.0] * len_tmp

            # 終了している場合の方策はパス
            if state.is_done():
                action_probs = [1.0]
            else:
                action_values = {}
                for action in state.legal_actions():
                    next_state = state.next(action=action, set_ratio=0)
                    na = board_idx_dict[(tuple(next_state.pieces), tuple(
                        next_state.enemy_pieces), next_state.depth % 2, next_state.pass_end)]
                    r = reward(state, next_state)
                    v = r + V[na]
                    action_values[action] = v

                if not state.is_first_player():
                    action_probs = set_argmax(
                        action_values, action_probs, state)
                else:
                    action_probs = set_argmin(
                        action_values, action_probs, state)
            pi[board_idx_dict[state_idx]] = action_probs
            cnt += 1
    print()
    return pi


def guess():
    V = value_iter()
    pi = greedy_policy(V)
    return V, pi


def play(V=None, pi=None, n=100, bisible=False):
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
                    print(V[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                    print(state.legal_actions())
                    print(pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
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

                # 行動の取得
                if state.is_first_player():
                    action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                else:
                    action = random_action(state)

                # 次の状態の取得
                state = state.next(action)

        print(f"[optimal vs randam] {black_win} : {white_win}")

        black_win = 0
        white_win = 0
        for _ in range(n):
            state = State()
            # ゲーム終了までループ
            while True:
                # ゲーム終了時

                # 文字列表示
                if bisible:
                    print(V[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                    print(state.legal_actions())
                    print(pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
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

                # 行動の取得
                if not state.is_first_player():
                    action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                else:
                    action = random_action(state)

                # 次の状態の取得
                state = state.next(action)

        print(f"[randam vs optimal] {black_win} : {white_win}")

        black_win = 0
        white_win = 0
        for _ in range(n):
            state = State()
            # ゲーム終了までループ
            while True:
                # ゲーム終了時

                # 文字列表示
                if bisible:
                    print(V[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                    print(state.legal_actions())
                    print(pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
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
                # 行動の取得
                if not state.is_first_player():
                    action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(tuple(state.pieces), tuple(
                        state.enemy_pieces), state.depth % 2, state.pass_end)]])
                else:
                    # action = random_action(state)
                    action = np.random.choice(state.legal_actions(), p=pi[board_idx_dict[(
                        tuple(state.pieces), tuple(state.enemy_pieces), state.depth % 2, state.pass_end)]])

                # 次の状態の取得
                state = state.next(action)

        print(f"[optimal vs optimal] {black_win} : {white_win}")


# 動作確認
if __name__ == '__main__':
    state = State()
    search(state=state)
    print()
    del state
    V, pi = guess()
    # write_data([V_2, pi_2, board_idx_dict])
    # history = load_data()
    # V_2 = history[0]
    # pi_2 = history[1]
    # board_idx_dict = history[2]

    play(V=V, pi=pi, n=10000, bisible=False)
