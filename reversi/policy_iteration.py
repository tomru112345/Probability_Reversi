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

    def set_pi(self, state: State, pi: defaultdict = None):
        if self.pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                              8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            self.pi[state] = tmp_d
        else:
            self.pi[state] == pi

    def get_pi(self, state: State, pi: defaultdict = None):
        if self.pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                              8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            return tmp_d
        else:
            return pi

    def eval_onestep(self, state: State):
        self.set_pi(state=state)
        if state.is_done():
            self.V[state] = 0  # 終了したときの価値関数は常に 0
            return self.V

        action_probs = self.pi[state]
        new_V = 0

        for action, action_prob in action_probs.items():
            next_state: State = state.next(action)
            self.get_pi(state=next_state)
            reward = first_player_value(state, next_state)
            new_V += action_prob * (reward + self.gamma * self.V[next_state])

        self.V[state] = new_V
        return self.V

    def policy_eval(self, state: State, threshold: float = 0.001):
        while True:
            old_V = self.V.copy()  # 更新前の価値関数
            self.V = self.eval_onestep(state)

            # 更新された量の最大値を求める
            delta = 0
            for state in self.V.keys():
                t = abs(self.V[state] - old_V[state])
                if delta < t:
                    delta = t

            # 値と比較
            if delta < threshold:
                break
        return self.V


    def greedy_policy(V, state: State, gamma):
        action_value = []

        action_list = state.legal_actions()
        for action in action_list:
            next_state = state.next(action)
            if next_state.is_done():
                if next_state.is_lose():
                    reward = 1
                elif next_state.is_draw():
                    reward = 0
                else:
                    reward = -1
            value = reward + gamma * V[next_state]
            action_value.append(value)
        a = np.array(action_value)
        max_action_index = np.argmax(a)
        return action_list[max_action_index]

# 動作確認
if __name__ == '__main__':
    # モデルの読み込み
    # 状態の生成
    state = State()
    agent_1 = Agent(flg=True)
    agent_2 = Agent(flg=False)
    agent_1.set_pi(state=state)
    agent_2.set_pi(state=state)

    agent_1.eval_onestep(state=state)
    # # ゲーム終了までループ
    # while True:
    #     # ゲーム終了時
    #     if state.is_done():
    #         break

    #     # 行動の取得
    #     action = next_action(state)
    #     # 次の状態の取得
    #     state = state.next(action)

    #     # 文字列表示
    #     print(state)
