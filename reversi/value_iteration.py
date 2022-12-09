from game import State
# from cppState import State
from settings import default_ratio_box
import sys
import itertools

sys.setrecursionlimit(10 ** 9)


def set_state(board):
    flg = board[16:]
    board = list(board[:16])
    pieces = [0] * 16
    enemy_pieces = [0] * 16
    for i in range(16):
        if board[i] == 1:
            pieces[i] = 1
        elif board[i] == -1:
            enemy_pieces[i] = 1
    if flg:
        state = State(pieces, enemy_pieces, default_ratio_box, 0)
    else:
        state = State(pieces, enemy_pieces, default_ratio_box, 1)
    return state


def set_board(state: State):
    board = [0] * 17
    for i in range(16):
        if state.pieces[i] == 1:
            board[i] = 1
        elif state.enemy_pieces[i] == 1:
            board[i] = -1
    if state.is_first_player():
        board[16] = True
    else:
        board[16] = False
    board = tuple(board)
    return board


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

all_board = []

def search(state: State, turn: int):
    global all_board
    # 全探索用
    now_board = set_board(state)
    all_board.append(now_board)
    for action in state.legal_actions():
        next_state = state.next(action=action)
        if state.is_done():
            continue
        else:
            search(next_state, turn+1)


def value_iter_onestep():
    # n_0 = [-1, 0, 1]
    # n_1 = [-1, 1]
    # bool_flg_l = [True, False]
    # all_board = tuple(itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
    #                                    n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0, bool_flg_l))
    # del n_0, n_1, bool_flg_l
    global all_board

    state = State()
    search(state=state, turn=0)
    del state
    V = [0] * 231301
    fin_flg_l = [(False, None)] * 231301

    # 初期化
    cnt = 0
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

    for board in all_board:
        print('\rinit {:,} / {:,}'.format(cnt + 1, 231301), end='')

        state = set_state(board)
        next_addr_l = []
        for action in set(state.legal_actions()):
            next_state = state.next(action)
            next_board = set_board(next_state)
            na = all_board.index(next_board)
            next_addr_l.append(na)
        next_addr_l = set(next_addr_l)

        piece_cnt = state.piece_count(state.pieces) + \
            state.piece_count(state.enemy_pieces)

        if check_fin(state=state):
            fin_flg_l[cnt] = (True, next_addr_l)
        else:
            if piece_cnt == 16:
                fin_flg_l[cnt] = (True, next_addr_l)
            elif piece_cnt == 4:
                adress_4.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 5:
                adress_5.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 6:
                adress_6.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 7:
                adress_7.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 8:
                adress_8.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 9:
                adress_9.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 10:
                adress_10.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 11:
                adress_11.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 12:
                adress_12.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 13:
                adress_13.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 14:
                adress_14.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)
            elif piece_cnt == 15:
                adress_15.append(cnt)
                fin_flg_l[cnt] = (False, next_addr_l)

        del state, board, piece_cnt, next_addr_l
        cnt += 1
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
    del adress_15, adress_14, adress_13, adress_12, adress_11, adress_10, adress_9, adress_8, adress_7, adress_6, adress_5, adress_4

    # 価値関数の設定
    cnt = 0
    stage = 15
    for i in range(13):
        for a in address[i]:
            print(
                '\rvalue_iter_onestep {:,} / {:,}: stage: {}'.format(cnt + 1, 164761, stage), end='')
            cnt += 1
            fin_flg, next_addrs = fin_flg_l[a]
            if fin_flg:
                del fin_flg, next_addrs
                continue

            else:
                state = set_state(all_board[a])
                if check_fin(state):
                    fin_flg_l[a] = (True, next_addrs)
                    del fin_flg, next_addrs
                    continue
                else:
                    action_values = []
                    for next_addr in next_addrs:
                        r = 0
                        if fin_flg_l[next_addr]:
                            r = reward(state)
                        v = r + (-1) * V[next_addr]
                        action_values.append(v)
                    V[a] = max(action_values)
                    del action_values, fin_flg, next_addrs
                del state
        stage -= 1
    return V


def main():
    V = value_iter_onestep()


    # 動作確認
if __name__ == '__main__':
    main()
