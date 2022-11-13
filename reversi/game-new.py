from cppState import State
import random
from settings import SQUARE, default_ratio_box


def random_action(state):
    """ランダムで行動選択"""
    legal_actions = state.legal_actions()
    return legal_actions[random.randint(0, len(legal_actions)-1)]


def print_reversi(state):
    """文字列表示"""
    ox = ('o', 'x') if state.is_first_player() else ('x', 'o')
    str = ''
    for i in range(SQUARE * SQUARE):
        if state.pieces[i] == 1:
            str += ox[0]
        elif state.enemy_pieces[i] == 1:
            str += ox[1]
        else:
            str += '-'
        if i % SQUARE == (SQUARE - 1):
            str += '\n'
    print(str)


if __name__ == '__main__':
    # 状態の生成
    state = State()
    # ゲーム終了までのループ
    # while True:
    #     # ゲーム終了時
    #     if state.is_done():
    #         break
    #     # 次の状態の取得
    #     state = state.next(random_action(state))
    #     # 文字列表示
    #     print_reversi(state)
    #     print()