# ====================
# 新パラメータ評価部
# ====================

# パッケージのインポート
import numpy as np
# from game import State
from cppState import State
# from pv_mcts import pv_mcts_action
from cppNode import pv_mcts_action
from keras.models import load_model
from keras import backend as K
from shutil import copy
from settings import default_ratio_box


# パラメータの準備
# EN_GAME_COUNT = 10  # 1評価あたりのゲーム数（本家は400）
EN_GAME_COUNT = 50
EN_TEMPERATURE = 1.0  # ボルツマン分布の温度


def first_player_point(ended_state: State):
    """先手プレイヤーのポイント"""
    # 1:先手勝利, 0:先手敗北, 0.5:引き分け
    if ended_state.is_lose():
        return 0 if ended_state.is_first_player() else 1
    return 0.5


def play(model0, model1, EN_TEMPERATURE):
    """1ゲームの実行"""
    # 状態の生成
    state = State(default_ratio_box)

    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 行動の取得
        if state.is_first_player():
            action = pv_mcts_action(model0, state, EN_TEMPERATURE)
        else:
            action = pv_mcts_action(model1, state, EN_TEMPERATURE)

        # 次の状態の取得
        state = state.next(action, np.random.rand())

    # 先手プレイヤーのポイントを返す
    return first_player_point(state)


def update_best_player():
    """ベストプレイヤーの交代"""
    copy(f'./model/latest.h5',
         f'./model/best.h5')
    print('Change BestPlayer')


def evaluate_network():
    """ネットワークの評価"""
    # 最新プレイヤーのモデルの読み込み
    model0 = load_model(f'./model/latest.h5')

    # ベストプレイヤーのモデルの読み込み
    model1 = load_model(f'./model/best.h5')

    # 複数回の対戦を繰り返す
    total_point = 0
    for i in range(EN_GAME_COUNT):
        # 1ゲームの実行
        if i % 2 == 0:
            total_point += play(model0, model1, EN_TEMPERATURE)
        else:
            total_point += 1 - play(model1, model0, EN_TEMPERATURE)

        # 出力
        print('\rEvaluate {}/{}'.format(i + 1, EN_GAME_COUNT), end='')
    print('')

    # 平均ポイントの計算
    average_point = total_point / EN_GAME_COUNT
    print('AveragePoint', average_point)

    # モデルの破棄
    K.clear_session()
    del model0
    del model1

    # ベストプレイヤーの交代
    if average_point > 0.5:
        update_best_player()
        return True
    else:
        return False


# 動作確認
if __name__ == '__main__':
    evaluate_network()
