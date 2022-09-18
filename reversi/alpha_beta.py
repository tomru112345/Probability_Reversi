# ====================
# アルファベータ法の作成
# ====================

# パッケージのインポート
from game import State, random_action
from pathlib import Path
import numpy as np
from settings import SQUARE
import os

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
# パラメータの準備
PV_EVALUATE_COUNT = 50  # 1推論あたりのシミュレーション回数（本家は1600）


def alpha_beta(state, alpha, beta):
    """アルファベータ法で状態価値計算"""
    # 負けは状態価値-1
    if state.is_lose():
        return -1

    # 引き分けは状態価値0
    if state.is_draw():
        return 0

    # 合法手の状態価値の計算
    for action in state.legal_actions():
        score = -alpha_beta(state.next(action), -beta, -alpha)
        if score > alpha:
            alpha = score

        # 現ノードのベストスコアが親ノードを超えたら探索終了
        if alpha >= beta:
            return alpha

    # 合法手の状態価値の最大値を返す
    return alpha


def alpha_beta_action(state):
    """アルファベータ法で行動選択"""
    # 合法手の状態価値の計算
    best_action = 0
    alpha = -float('inf')
    str = ['', '']
    for action in state.legal_actions():
        score = -alpha_beta(state.next(action), -float('inf'), -alpha)
        if score > alpha:
            best_action = action
            alpha = score

        str[0] = '{}{:2d},'.format(str[0], action)
        str[1] = '{}{:2d},'.format(str[1], score)
    print('action:', str[0], '\nscore: ', str[1], '\n')

    # 合法手の状態価値の最大値を持つ行動を返す
    return best_action


# 動作確認
if __name__ == '__main__':
    # 状態の生成
    state = State()

    # ゲーム終了までのループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 行動の取得
        if state.is_first_player():
            action = alpha_beta_action(state)
        else:
            action = random_action(state)

        # 次の状態の取得
        state = state.next(action)

        # 文字列表示
        print(state)
        print()
