# ====================
# TD学習の作成
# ====================

# パッケージのインポート
from collections import defaultdict
from game import State
from dual_network import DN_INPUT_SHAPE, DN_OUTPUT_SIZE
from math import sqrt
from keras.models import load_model
from pathlib import Path
import numpy as np
from settings import SQUARE

# パラメータの準備
PV_EVALUATE_COUNT = 50  # 1推論あたりのシミュレーション回数（本家は1600）


def predict(model, state: State):
    """推論"""
    # 推論のための入力データのシェイプの変換
    a, b, c = DN_INPUT_SHAPE

    x = np.array([state.pieces, state.enemy_pieces, state.ratio_box])
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c)

    # 推論
    y = model.predict(x, batch_size=1)

    # 方策の取得
    policies = y[0][0][list(state.legal_actions())]  # 合法手のみ
    policies /= sum(policies) if sum(policies) else 1  # 合計1の確率分布に変換

    # 価値の取得
    value = y[1][0][0]
    return policies, value


def nodes_to_scores(nodes):
    """ノードのリストを試行回数のリストに変換"""
    scores = []
    for c in nodes:
        scores.append(c.n)
    return scores


def pv_mcts_scores(model, state, temperature):
    """モンテカルロ木探索のスコアの取得"""
    class Node:
        """モンテカルロ木探索のノードの定義"""

        def __init__(self, state, p):
            """ノードの初期化"""
            self.state = state  # 状態
            self.p = p  # 方策
            self.w = 0  # 累計価値
            self.n = 0  # 試行回数
            self.child_nodes = None  # 子ノード群

            # TODO
            self.V = defaultdict(lambda: 0)

        def evaluate(self):
            """局面の価値の計算"""
            # ゲーム終了時
            if self.state.is_done():
                # 勝敗結果で価値を取得
                value = -1 if self.state.is_lose() else 0

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1
                return value

            # 子ノードが存在しない時
            if not self.child_nodes:
                # ニューラルネットワークの推論で方策と価値を取得
                policies, value = predict(model, self.state)

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1

                # 子ノードの展開
                self.child_nodes = []
                for action, policy in zip(self.state.legal_actions(), policies):
                    self.child_nodes.append(
                        Node(self.state.next(action), policy))
                return value

            # 子ノードが存在する時
            else:
                # アーク評価値が最大の子ノードの評価で価値を取得
                value = -self.next_child_node().evaluate()

                # 累計価値と試行回数の更新
                self.w += value
                self.n += 1
                return value

        def next_child_node(self):
            """アーク評価値が最大の子ノードを取得"""
            # アーク評価値の計算
            C_PUCT = 1.0
            t = sum(nodes_to_scores(self.child_nodes))

            pucb_values = []
            for child_node in self.child_nodes:
                pucb_values.append((-child_node.w / child_node.n if child_node.n else 0.0) +
                                   C_PUCT * child_node.p * sqrt(t) / (1 + child_node.n))

            # アーク評価値が最大の子ノードを返す
            return self.child_nodes[np.argmax(pucb_values)]

    # 現在の局面のノードの作成
    root_node = Node(state, 0)

    # 複数回の評価の実行
    for _ in range(PV_EVALUATE_COUNT):
        root_node.evaluate()

    # 合法手の確率分布
    scores = nodes_to_scores(root_node.child_nodes)
    if temperature == 0:  # 最大値のみ1
        action = np.argmax(scores)
        scores = np.zeros(len(scores))
        scores[action] = 1
    else:  # ボルツマン分布でバラつき付加
        scores = boltzman(scores, temperature)
    return scores


def pv_mcts_action(model, temperature=0):
    """モンテカルロ木探索で行動選択"""
    def pv_mcts_action(state):
        scores = pv_mcts_scores(model, state, temperature)
        return np.random.choice(state.legal_actions(), p=scores)
    return pv_mcts_action


def pv_mcts_action_policy(model, temperature=0):
    """モンテカルロ木探索で行動選択+盤面の方策の出力"""
    def pv_mcts_action_policy(state):
        scores = pv_mcts_scores(model, state, temperature)

        # 学習データに状態と方策を追加
        policies = [0] * DN_OUTPUT_SIZE
        for action, policy in zip(state.legal_actions(), scores):
            policies[action] = policy
        policies = policies[:DN_OUTPUT_SIZE - 1]
        return np.random.choice(state.legal_actions(), p=scores), policies
    return pv_mcts_action_policy


def boltzman(xs, temperature):
    """ボルツマン分布"""
    xs = [x ** (1 / temperature) for x in xs]
    return [x / sum(xs) for x in xs]


# 動作確認
if __name__ == '__main__':
    # モデルの読み込み
    path = sorted(Path(f'./model/{SQUARE}x{SQUARE}/').glob('*.h5'))[-1]
    model = load_model(str(path))

    # 状態の生成
    state = State()

    # モンテカルロ木探索で行動取得を行う関数の生成
    next_action = pv_mcts_action(model, 1.0)

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
        print(state)
