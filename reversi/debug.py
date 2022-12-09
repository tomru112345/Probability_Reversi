from game import State
# from cppState import State
from settings import default_ratio_box


def reward(state: State):
    if state.piece_count(state.pieces) == state.piece_count(state.enemy_pieces):
        return 0
    elif state.piece_count(state.pieces) > state.piece_count(state.enemy_pieces):
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

adress_4 = []
adress_5 = []
adress_6 = []
adress_7 = []
adress_8 = []
adress_9 = []
adress_10 = []
adress_11 = []
adress_12 = []
adress_13 = []
adress_14 = []
adress_15 = []

all_board = [None] * 63665
fin_flg_l = [False] * 63665
all_board_d = {}


def search(state: State, turn: int):
    global all_board_d, cnt, fin_flg_l, adress_15, adress_14, adress_13, adress_12, adress_11, adress_10, adress_9, adress_8, adress_7, adress_6, adress_5, adress_4
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
            adress_4.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 5:
            adress_5.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 6:
            adress_6.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 7:
            adress_7.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 8:
            adress_8.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 9:
            adress_9.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 10:
            adress_10.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 11:
            adress_11.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 12:
            adress_12.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 13:
            adress_13.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 14:
            adress_14.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        elif piece_cnt == 15:
            adress_15.append((tuple(state.pieces), tuple(
                state.enemy_pieces), state.depth % 2))
        if state.is_done():
            fin_flg_l[cnt] = True
            return
        else:
            for action in state.legal_actions():
                next_state = state.next(action=action)
                search(next_state, turn+1)


def value_iter_onestep():
    global all_board_d, cnt, fin_flg_l, adress_15, adress_14, adress_13, adress_12, adress_11, adress_10, adress_9, adress_8, adress_7, adress_6, adress_5, adress_4
    V = [0] * 63665
    state = State()
    search(state=state, turn=0)
    print()
    address = [
        tuple(adress_15),
        tuple(adress_14),
        tuple(adress_13),
        tuple(adress_12),
        tuple(adress_11),
        tuple(adress_10),
        tuple(adress_9),
        tuple(adress_8),
        tuple(adress_7),
        tuple(adress_6),
        tuple(adress_5),
        tuple(adress_4),
    ]
    del state
    del adress_15, adress_14, adress_13, adress_12, adress_11, adress_10, adress_9, adress_8, adress_7, adress_6, adress_5, adress_4

    # # 価値関数の設定
    cnt = 0
    stage = 15
    for i in range(12):
        for a in address[i]:
            print(
                '\rvalue_iter_onestep {:,} / {:,}: stage: {}'.format(cnt + 1, 58613, stage), end='')
            cnt += 1
            if fin_flg_l[all_board_d[a]]:
                continue
            else:
                action_values = []
                pieces, enemy_pieces, depth = all_board[all_board_d[a]]
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
                V[all_board_d[a]] = max(action_values)
                del action_values, state
        stage -= 1
    return V


value_iter_onestep()
