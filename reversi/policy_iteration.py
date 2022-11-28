from game import State
from collections import defaultdict
import numpy as np


def first_player_value(state, next_state):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if not state.is_lose():
        if next_state.is_lose():
            return -1.0 if next_state.is_first_player() else 1.0
    return 0.0


class Agent:
    def __init__(self, state: State) -> None:
        """初期化"""
        self.gamma = 0.9
        self.agent_state = [state.pieces, state.enemy_pieces, state.ratio_box]
        self.pi = defaultdict(State)
        self.V = defaultdict(lambda: 0)
        self.flg_first_player = state.is_first_player()

    def set_agent_state(self, state: State):
        """エージェントの盤面状態の更新"""
        self.agent_state = [state.pieces, state.enemy_pieces, state.ratio_box]

    def eval_onestep(self, state: State):
        self.set_agent_state(state=state)
        if state.is_done():
            self.V[self.agent_state] = 0  # 終了したときの価値関数は常に 0
            return self.V

        action_probs = self.pi[self.agent_state]
        new_V = 0

        for action, action_prob in action_probs.items():
            next_state: State = state.next(action)
            reward = first_player_value(state, next_state)
            new_V += action_prob * (reward + self.gamma * self.V[next_state])

        self.V[state] = new_V
        pass


def policy_eval(pi, V, state: State, gamma: float = 0.9, threshold: float = 0.001):
    while True:
        old_V = V.copy()
        pass


def greedy_policy(V, state, gamma):
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
