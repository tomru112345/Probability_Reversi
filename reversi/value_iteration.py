from game import State
from collections import defaultdict
import numpy as np


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


def value_iter_onestep(V: defaultdict, state: State, gamma: float, flg: bool = True):

    for action, action_prob in action_probs.items():
        next_state: State = state.next(action)
        if state.is_first_player() == flg:
            reward = first_player_value(state, next_state)
        else:
            reward = - (first_player_value(state, next_state))
        new_V += action_prob * (reward + gamma * V[next_state])

    V[state] = new_V
    return V


def policy_eval(pi: defaultdict, V: defaultdict, state: State, gamma: float, threshold: float = 0.001, flg: bool = True):
    while True:
        old_V = V.copy()  # 更新前の価値関数
        V = eval_onestep(pi, V, state, gamma, flg)
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


def greedy_policy(pi: defaultdict, V: defaultdict, state: State, gamma: float, flg: bool = True):

    pi_value = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}

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
    pi_value[max_action] = 1.0
    return pi_value


def policy_iter(pi: defaultdict, V: defaultdict, state: State, gamma: float, threshold: float = 0.001, flg: bool = True):
    while True:
        V = policy_eval(pi, V, state=state, gamma=gamma,
                        threshold=threshold, flg=flg)
        new_pi = greedy_policy(pi, V, state=state, gamma=gamma, flg=flg)

        if new_pi == pi[state]:
            break
        pi[state] = new_pi
    return pi, V


def main(num):
    agent_1 = Agent(flg=False)
    for i in range(num):
        state = State()
        while True:
            # ゲーム終了時
            if state.is_done():
                break

            agent_1.set_pi(state)
            print(agent_1.pi[state])
            pi, V = policy_iter(agent_1.pi, agent_1.V, state,
                                gamma=0.9, flg=agent_1.flg_first_player)
            agent_1.pi = pi
            agent_1.V = V

            d = agent_1.pi[state]
            l_i = []
            l_d = []
            for a, b in d.items():
                l_i.append(a)
                l_d.append(b)
            state = state.next(np.random.choice(l_i, p=l_d))
            # print(state)


    # 動作確認
if __name__ == '__main__':
    # モデルの読み込み
    # 状態の生成
    main(1)
