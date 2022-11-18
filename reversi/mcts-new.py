# ====================
# モンテカルロ木探索の作成
# ====================

# 参考コード
# https://zenn.dev/ganariya/articles/python-monte-carlo-tree-search

# パッケージのインポート
from dual_network import DN_INPUT_SHAPE
from typing import Optional, List
from keras.models import Model, load_model
from pathlib import Path
import numpy as np
from math import sqrt
from settings import SQUARE, default_ratio_box
import watch
from cppState import State
from cppMCTS import *


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
    # モデルの読み込み
    path = sorted(Path(f'./model/').glob('*.h5'))[-1]
    model = load_model(str(path))

    # 状態の生成
    state = State(default_ratio_box)

    # モンテカルロ木探索で行動取得を行う関数の生成
    # next_action = pv_mcts_action(model, state, 1.0)

    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 行動の取得
        action = pv_mcts_action(model, state, 1.0)

        # 次の状態の取得
        state = state.next(action)

        # 文字列表示
        print_reversi(state)
        # print(state)
