# ====================
# モンテカルロ木探索の作成
# ====================

# 参考コード
# https://zenn.dev/ganariya/articles/python-monte-carlo-tree-search

# パッケージのインポート
from dual_network import DN_INPUT_SHAPE, DN_OUTPUT_SIZE
from keras.models import Model, load_model
from pathlib import Path
import numpy as np
from settings import SQUARE, default_ratio_box
from cppState import State
from cppNode import Node
import os
import watch

# tensorflow の warning の設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# パラメータの準備
# PV_EVALUATE_COUNT = 50  # 1推論あたりのシミュレーション回数（本家は1600）
PV_EVALUATE_COUNT = 12


def pv_mcts_scores(model: Model, state: State, temperature: float):
    """モンテカルロ木探索のスコアの取得"""
    # 現在の局面のノードの作成
    root_node = Node(model, state, 0)

    # 複数回の評価の実行
    for _ in range(PV_EVALUATE_COUNT):
        root_node.evaluate()
        # evaluate(root_node)

    # 合法手の確率分布
    scores = root_node.nodes_to_scores()
    if temperature == 0:  # 最大値のみ1
        action = np.argmax(scores)
        scores = np.zeros(len(scores))
        scores[action] = 1
    else:  # ボルツマン分布でバラつき付加
        scores = boltzman(scores, temperature)
    return scores


def pv_mcts_action(model, temperature=0):
    """モンテカルロ木探索で行動選択"""
    # @watch.watch
    def pv_mcts_action(state):
        scores = pv_mcts_scores(model, state, temperature)
        return np.random.choice(a=state.legal_actions(), p=scores)
    return pv_mcts_action


def boltzman(xs, temperature):
    """ボルツマン分布"""
    xs = [x ** (1 / temperature) for x in xs]
    return [x / sum(xs) for x in xs]


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


@watch.watch
def main(n):
    """動作確認"""
    for _ in range(n):
        # モデルの読み込み
        path = sorted(Path(f'./model/').glob('*.h5'))[-1]
        model = load_model(str(path))

        # 状態の生成
        state = State(default_ratio_box)

        # モンテカルロ木探索で行動取得を行う関数の生成
        next_action = pv_mcts_action(model, 1.0)
        # next_action = pv_mcts_action(model, state, 1.0)
        # print_reversi(state)
        # ゲーム終了までループ
        while True:
            # ゲーム終了時
            if state.is_done():
                break

            # 行動の取得
            action = next_action(state)
            # 次の状態の取得
            state = state.next(action)

            # 文字列表示
            # print_reversi(state)


if __name__ == '__main__':
    main(1)
