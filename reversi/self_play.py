# ====================
# セルフプレイ部
# ====================

# パッケージのインポート
# from game import State
from cppState import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
from keras.models import load_model
from keras import backend as K
import numpy as np
import pickle
import os
from settings import default_ratio_box

# パラメータの準備
# SP_GAME_COUNT = 500  # セルフプレイを行うゲーム数（本家は25000）
SP_GAME_COUNT = 1000
SP_TEMPERATURE = 1.0  # ボルツマン分布の温度パラメータ


def first_player_value(ended_state):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if ended_state.is_lose():
        return -1 if ended_state.is_first_player() else 1
    return 0


def write_data(history):
    """学習データの保存"""
    now = datetime.now()
    os.makedirs(f'./data/', exist_ok=True)  # フォルダがない時は生成
    path = './data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    with open(path, mode='wb') as f:
        pickle.dump(history, f)


def play(model):
    """1ゲームの実行"""
    # 学習データ
    history = []

    # 状態の生成
    state = State(default_ratio_box)

    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 合法手の確率分布の取得
        scores = pv_mcts_scores(model, state, SP_TEMPERATURE)

        # 学習データに状態と方策を追加
        policies = [0] * DN_OUTPUT_SIZE
        for action, policy in zip(state.legal_actions(), scores):
            policies[action] = policy
        # history.append([[state.pieces, state.enemy_pieces], policies, None])
        history.append(
            [[state.pieces, state.enemy_pieces, state.ratio_box], policies, 0])

        # 行動の取得
        action = np.random.choice(state.legal_actions(), p=scores)
        # 次の状態の取得
        state = state.next(action)

    # 学習データに価値を追加
    value = first_player_value(state)
    for i in range(len(history)):
        history[i][2] += value
        value = -value
    return history


def self_play():
    """セルフプレイ"""
    # 学習データ
    history = []

    # ベストプレイヤーのモデルの読み込み
    model = load_model(f'./model/best.h5')

    # 複数回のゲームの実行
    for i in range(SP_GAME_COUNT):
        # 1ゲームの実行
        h = play(model)
        history.extend(h)

        # ログ出力
        print('\rSelfPlay {}/{}'.format(i + 1, SP_GAME_COUNT), end='')
    print('')

    # 学習データの保存
    write_data(history)

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == '__main__':
    self_play()
