from game import State
# from cppState import State
from collections import defaultdict
from settings import default_ratio_box
from typing import List
from datetime import datetime
from pathlib import Path
import sys
import pickle
import os
import itertools

sys.setrecursionlimit(10 ** 9)


def write_data(history):
    """学習データの保存"""
    now = datetime.now()
    os.makedirs(f'./policy_iteration_data/', exist_ok=True)  # フォルダがない時は生成
    path = './policy_iteration_data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    with open(path, mode='wb') as f:
        pickle.dump(history, f)


def load_data():
    """学習データの読み込み"""
    history_path = sorted(
        Path(f'./policy_iteration_data/').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


gamma = 0.9


def init_pi_v():
    pi = defaultdict(lambda: {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                              7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0})
    V = defaultdict(lambda: 0)

    n_0 = [-1, 0, 1]
    n_1 = [-1, 1]
    all_board = list(itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                                       n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0))

    states: List[State] = []
    for board in all_board:
        board = list(board)
        pieces = [0] * 16
        enemy_pieces = [0] * 16
        for i in range(16):
            if board[i] == 1:
                pieces[i] = 1
            elif board[i] == -1:
                enemy_pieces[i] = 1
        state = State(pieces, enemy_pieces, default_ratio_box, 0)
        if pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            pi[state] = tmp_d
        V[state] = 0
        states.append(state)
        state = State(pieces, enemy_pieces, default_ratio_box, 1)
        if pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            pi[state] = tmp_d
        V[state] = 0
        states.append(state)
        del state, pieces, enemy_pieces, board
    del all_board, n_0, n_1

    pi = dict(pi)
    V = dict(V)

    history = [states, pi, V]
    write_data(history)
    del history


# init_pi_v()
history = load_data()
# print(type(history[0]))
# print(type(history[1]))
# print(type(history[2]))
states: List[State] = history[0]
pi: dict = history[1]
V: dict = history[2]


def first_player_value(state: State, next_state: State):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if not state.is_done():
        if next_state.is_lose():
            return -1.0 if next_state.is_first_player() else 1.0
    return 0.0


def eval_onestep(pi: dict, V: dict, gamma: float, flg: bool = True):
    """反復方策評価の 1 ステップ"""
    print("eval_onestep start")
    for state in states:
        if state.is_done():
            V[state] = 0  # 終了したときの価値関数は常に 0
            continue

        action_probs: dict = pi[state]
        new_V = 0
        for action in state.legal_actions():
            next_state: State = state.next(action)
            if flg:
                reward = first_player_value(state, next_state)
            else:
                reward = - (first_player_value(state, next_state))
            new_V += action_probs[action] * (reward + gamma * V[next_state])
        V[state] = new_V
        del action_probs, state, next_state, new_V, reward
    print("eval_onestep finish")
    return V


def policy_eval(pi: dict, V: dict, gamma: float, threshold: float = 0.001, flg: bool = True):
    """方策評価"""
    print("policy_eval start")
    while True:
        old_V = V.copy()  # 更新前の価値関数
        V = eval_onestep(pi, V, gamma, flg)
        # 更新された量の最大値を求める
        delta = 0
        for state in V.keys():
            t = abs(V[state] - old_V[state])
            if delta < t:
                delta = t
            del state
        # 値と比較
        if delta < threshold:
            break
    print("policy_eval finish")
    return V


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def greedy_policy(V: defaultdict, gamma: float, flg: bool = True):
    """greedy 方策"""
    print("greedy_policy start")
    pi = {}
    for state in states:
        action_values = {}
        for action in state.legal_actions():
            next_state = state.next(action)
            if state.is_first_player() == flg:
                reward = first_player_value(state, next_state)
            else:
                reward = - (first_player_value(state, next_state))
            value = reward + gamma * V[next_state]
            action_values[action] = value
        max_action = argmax(action_values)
        action_probs = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                        8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}
        action_probs[max_action] = 1.0
        pi[state] = action_probs
        del action_probs
    print("greedy_policy finish")
    return pi


def policy_iter(pi: defaultdict, V: defaultdict, gamma: float, threshold: float = 0.001, flg: bool = True):
    """方策反復法"""
    while True:
        history = []
        V = policy_eval(pi, V, gamma=gamma, threshold=threshold, flg=flg)
        new_pi = greedy_policy(V, gamma=gamma, flg=flg)
        if new_pi == pi:
            break
        pi = new_pi
        pi = dict(pi)
        V = dict(V)
        history.append([pi, V])
        write_data(history)
        del history
    return pi, V


def main(pi, V, gamma, flg):
    # 状態の生成
    new_pi, new_V = policy_iter(pi=pi, V=V, gamma=gamma, flg=flg)


main(pi, V, gamma, True)
