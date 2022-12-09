from game import State
# from cppState import State
from settings import default_ratio_box
import sys
import numpy as np

sys.setrecursionlimit(10 ** 9)


def reward(state: State):
    if state.piece_count(state.pieces) == state.piece_count(state.enemy_pieces):
        return 0
    elif state.piece_count(state.pieces) < state.piece_count(state.enemy_pieces):
        return 1
    else:
        return -1


def check_fin(state: State):
    if state.piece_count(state.pieces) + state.piece_count(state.enemy_pieces) == 16:
        return True
    elif state.piece_count(state.pieces) == 0:
        return True
    elif state.piece_count(state.enemy_pieces) == 0:
        return True
    elif state.legal_actions() == [16]:
        next_state = state.next(16)
        if next_state.legal_actions() == [16]:
            return True
        else:
            return False
    else:
        return False


cnt = -1

state_4 = []
state_5 = []
state_6 = []
state_7 = []
state_8 = []
state_9 = []
state_10 = []
state_11 = []
state_12 = []
state_13 = []
state_14 = []
state_15 = []

all_board = [None] * 63665
fin_flg_l = [False] * 63665
all_board_d = {}


def search(state: State, turn: int):
    global all_board, all_board_d, cnt, fin_flg_l, state_15, state_14, state_13, state_12, state_11, state_10, state_9, state_8, state_7, state_6, state_5, state_4
    if not (tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2) in all_board_d:
        cnt += 1
        print('\rinit {:,} / {:,}'.format(cnt + 1, 63665), end='')
        all_board_d[(tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2)] = cnt
        all_board[cnt] = (state.pieces, state.enemy_pieces, state.depth % 2)
        piece_cnt = state.piece_count(state.pieces) + \
            state.piece_count(state.enemy_pieces)
        if piece_cnt == 4:
            state_4.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 5:
            state_5.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 6:
            state_6.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 7:
            state_7.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 8:
            state_8.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 9:
            state_9.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 10:
            state_10.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 11:
            state_11.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 12:
            state_12.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 13:
            state_13.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 14:
            state_14.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 15:
            state_15.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))

        if state.is_done():
            fin_flg_l[cnt] = True
            return
        else:
            for action in state.legal_actions():
                next_state = state.next(action=action)
                search(next_state, turn+1)


def value_iter_onestep():
    global all_board_d, cnt, fin_flg_l, state_15, state_14, state_13, state_12, state_11, state_10, state_9, state_8, state_7, state_6, state_5, state_4
    V = [0] * 63665
    state = State()
    search(state=state, turn=0)
    print()
    states_num_l = [
        tuple(state_15),
        tuple(state_14),
        tuple(state_13),
        tuple(state_12),
        tuple(state_11),
        tuple(state_10),
        tuple(state_9),
        tuple(state_8),
        tuple(state_7),
        tuple(state_6),
        tuple(state_5),
        tuple(state_4),
    ]
    del state
    del state_15, state_14, state_13, state_12, state_11, state_10, state_9, state_8, state_7, state_6, state_5, state_4

    # # 価値関数の設定
    cnt = 0
    stage = 15
    for i in range(12):
        for states_num in states_num_l[i]:
            print(
                '\rvalue_iter_onestep {:,} / {:,}'.format(cnt + 1, 58613), end='')
            cnt += 1
            if fin_flg_l[all_board_d[states_num]]:
                continue
            else:
                action_values = []
                pieces, enemy_pieces, depth = all_board[all_board_d[states_num]]
                state: State = State(pieces, enemy_pieces,
                                     default_ratio_box, depth % 2)
                for action in state.legal_actions():
                    next_state = state.next(action)
                    na = all_board_d[(tuple(next_state.pieces), tuple(
                        next_state.enemy_pieces), next_state.depth % 2)]
                    r = 0
                    if fin_flg_l[na]:
                        r = reward(state)
                    v = r + (-1) * V[na]
                    action_values.append(v)
                V[all_board_d[states_num]] = max(action_values)
                del action_values, state
        stage -= 1
    print()
    return V


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def greedy_policy(V):
    global all_board, all_board_d
    pi = [0] * 63665
    # # 価値関数の設定
    for i in range(63665):
        print(
            '\rgreedy_policy {:,} / {:,}'.format(i + 1, 63665), end='')
        pieces, enemy_pieces, depth = all_board[i]
        state: State = State(pieces, enemy_pieces,
                             default_ratio_box, depth % 2)
        len_tmp = len(state.legal_actions())
        action_probs = [0.0] * len_tmp
        if state.is_done():
            action_probs = [1.0]
        else:
            action_values = {}
            for action in state.legal_actions():
                next_state = state.next(action)
                na = all_board_d[(tuple(next_state.pieces), tuple(
                    next_state.enemy_pieces), next_state.depth % 2)]
                r = 0
                if fin_flg_l[na]:
                    r = reward(state)
                v = r + (-1) * V[na]
                action_values[action] = v
            max_action = argmax(action_values)
            action_probs[state.legal_actions().index(max_action)] = 1.0
        pi[i] = action_probs
    print()
    return pi


def main():
    global all_board_d
    V = value_iter_onestep()
    pi = greedy_policy(V)
    state = State()
    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 行動の取得
        index_state = all_board_d[(tuple(state.pieces), tuple(
            state.enemy_pieces), state.depth % 2)]
        action_probs = list(pi[index_state])
        action = np.random.choice(state.legal_actions(), p=action_probs)
        # 次の状態の取得
        state = state.next(action)

        # 文字列表示
        print(state)


    # 動作確認
if __name__ == '__main__':
    main()
