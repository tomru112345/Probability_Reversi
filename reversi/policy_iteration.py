# from game import State
from cppState import State
from collections import defaultdict
from settings import SQUARE, default_ratio_box
import numpy as np
from typing import List
import random
import sys
import itertools

sys.setrecursionlimit(10 ** 9)

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
            enemy_pieces[i] = -1
    state = State(pieces=pieces, enemy_pieces=enemy_pieces,
                  ratio_box=default_ratio_box, depth=0)
    states.append(state)
    del state, pieces, enemy_pieces

# print(len(states))


def first_player_value(state: State, next_state: State):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if not state.is_lose():
        if next_state.is_lose():
            return -1.0 if next_state.is_first_player() else 1.0
    return 0.0


class Agent:
    def __init__(self, flg: bool):
        """初期化"""
        self.gamma = 0.9
        self.pi = defaultdict(lambda: {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                              7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0})
        self.V = defaultdict(lambda: 0)
        self.flg_first_player = flg

    def set_pi(self, state: State):
        if self.pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                              7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            self.pi[state] = tmp_d


def eval_onestep(pi: defaultdict, V: defaultdict, gamma: float, flg: bool = True):
    """反復方策評価の 1 ステップ"""
    print("a")
    for state in states:
        if state.is_done():
            V[state] = 0  # 終了したときの価値関数は常に 0
            continue

        action_probs: defaultdict = pi[state]
        new_V = 0
        for action, action_prob in action_probs.items():
            next_state: State = state.next(action)
            if flg:
                reward = first_player_value(state, next_state)
            else:
                reward = - (first_player_value(state, next_state))
            new_V += action_prob * (reward + gamma * V[next_state])
        V[state] = new_V
        del action_probs, state, next_state
    print("b")
    return V


def policy_eval(pi: defaultdict, V: defaultdict, gamma: float, threshold: float = 0.001, flg: bool = True):
    """方策評価"""
    while True:
        old_V = V.copy()  # 更新前の価値関数
        V = eval_onestep(pi, V, gamma, flg)
        # 更新された量の最大値を求める
        delta = 0
        for state in V.keys():
            t = abs(V[state] - old_V[state])
            if delta < t:
                delta = t

        # 値と比較
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


def greedy_policy(V: defaultdict, gamma: float, flg: bool = True):
    """greedy 方策"""
    pi = {}
    for state in states:
        action_values = {}
        action_list = state.legal_actions()
        for action in action_list:
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
    return pi


def policy_iter(pi: defaultdict, V: defaultdict, gamma: float, threshold: float = 0.001, flg: bool = True):
    """方策反復法"""
    while True:
        V = policy_eval(pi, V, gamma=gamma, threshold=threshold, flg=flg)
        new_pi = greedy_policy(V, gamma=gamma, flg=flg)
        if new_pi == pi:
            break
        pi = new_pi
    return pi, V


def main():
    # 状態の生成
    agent_1 = Agent(flg=True)
    new_pi, new_V = policy_iter(
        pi=agent_1.pi, V=agent_1.V, gamma=agent_1.gamma, flg=agent_1.flg_first_player)
    agent_1.pi = new_pi
    agent_1.V = new_V
    print(agent_1.pi)

    # for i in range(num):
    #     state = State()
    #     while True:
    #         # ゲーム終了時
    #         if state.is_done():
    #             break

    #         agent_1.set_pi(state)
    #         print(agent_1.pi[state])
    #         pi, V = policy_iter(agent_1.pi, agent_1.V, state,
    #                             gamma=0.9, flg=agent_1.flg_first_player)
    #         agent_1.pi = pi
    #         agent_1.V = V

    #         d: dict = agent_1.pi[state]
    #         l_i = []
    #         l_d = []
    #         for a, b in d.items():
    #             l_i.append(a)
    #             l_d.append(b)
    #         state = state.next(np.random.choice(l_i, p=l_d))
    #         # print(state)


    # 動作確認
    # if __name__ == '__main__':
    # モデルの読み込み
    # 状態の生成
main()
# state = State()
# rs = Reversi_State(state=state)
# print(rs.state)
