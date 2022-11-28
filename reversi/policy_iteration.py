from game import State
from collections import defaultdict
import numpy as np


pi = defaultdict(State)
V = defaultdict(lambda: 0)
gamma = 0.9


def eval_onestep(pi, V, state: State, gamma: float = 0.9):
    if state.is_done():
        V.append(0)  # 終了したときの価値関数は常に 0
        return V

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
