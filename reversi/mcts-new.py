# ====================
# モンテカルロ木探索の作成
# ====================

# 参考コード
# https://zenn.dev/ganariya/articles/python-monte-carlo-tree-search

# パッケージのインポート
from game import State
from dual_network import DN_INPUT_SHAPE
from typing import Optional, List
from keras.models import Model, load_model
from pathlib import Path
import numpy as np
from math import sqrt
from settings import SQUARE
import watch

# パラメータの準備
PV_EVALUATE_COUNT = 50  # 1推論あたりのシミュレーション回数（本家は1600）


def predict(model: Model, state: State):
    """推論"""
    # 推論のための入力データのシェイプの変換
    a, b, c = DN_INPUT_SHAPE
    x = np.array([state.pieces, state.enemy_pieces, state.ratio_box])
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c)

    # 推論
    y = model.predict(x=x, batch_size=1)

    # 方策の取得
    policies = y[0][0][list(state.legal_actions())]  # 合法手のみ
    policies /= sum(policies) if sum(policies) else 1  # 合計1の確率分布に変換

    # 価値の取得
    value = y[1][0][0]
    return policies, value


def nodes_to_scores(nodes: List["Node"]) -> List[float]:
    """ノードのリストを試行回数のリストに変換"""
    # scores = []
    # for c in nodes:
    #     scores.append(c.n)
    scores = [c. n for c in nodes]
    return scores


class Node:
    """ノードの定義"""

    def __init__(self, model: Model, state: State, p: int, expand_base: int = 10) -> None:
        self.model = model  # 学習モデル
        self.state: State = state  # 状態
        self.p = p  # 方策
        self.w: int = 0  # 累計価値
        self.n: int = 0  # 試行回数
        self.child_nodes: Optional[List[Node]] = None  # 子ノード群
        self.expand_base: int = expand_base

    def evaluate(self) -> float:
        """局面 (self: current Node) の評価値の計算, 更新"""
        if self.state.is_done():  # ゲーム終了時
            value = -1 if self.state.is_lose() else 0  # 勝敗結果で価値を取得

            # 累計価値と試行回数の更新
            self.w += value
            self.n += 1
            return value

        # self (current Node) に子ノードがない場合
        # 子ノードが存在しない時
        if not self.child_nodes:
            # ニューラルネットワークの推論で方策と価値を取得
            policies, value = predict(self.model, self.state)
            # 累計価値と試行回数の更新
            self.w += value
            self.n += 1
            # 子ノードの展開
            # self.child_nodes = []
            # 十分に self (current Node) がプレイされたら展開(1ノード掘り進める)する
            # if self.n == self.expand_base:
            #     self.child_nodes = [Node(self.state.next(action), p=policy, expand_base=self.expand_base)
            #                         for action, policy in zip(self.state.legal_actions(), policies)]

            self.child_nodes = [Node(model=self.model, state=self.state.next(action), p=policy, expand_base=self.expand_base)
                                for action, policy in zip(self.state.legal_actions(), policies)]
            # for action, policy in zip(self.state.legal_actions(), policies):
            #     self.child_nodes.append(
            #         Node(state=self.state.next(action), p=policy, expand_base=self.expand_base))
            return value
        else:
            # アーク評価値が最大の子ノードの評価で価値を取得
            value = -self.next_child_node().evaluate()
            # 累計価値と試行回数の更新
            self.w += value
            self.n += 1
            return value

    def next_child_node(self) -> "Node":
        """アーク評価値が最大の子ノードを取得"""
        # アーク評価値の計算
        C_PUCT = 1.0
        t = sum(nodes_to_scores(self.child_nodes))

        pucb_values = []
        for child_node in self.child_nodes:
            if child_node.n == 0:  # 試行回数が0のノードを優先的に選ぶ
                return child_node
            else:
                pucb_values.append((-child_node.w / child_node.n if child_node.n else 0.0) +
                                   C_PUCT * child_node.p * sqrt(t) / (1 + child_node.n))
        return self.child_nodes[np.argmax(pucb_values)]  # アーク評価値が最大の子ノードを返す


class MCTS:
    """モンテカルロ木探索クラス"""

    def __init__(self, temperature: float = 0) -> None:
        self.temperature = temperature

    def boltzman(self, xs: List[float]) -> List[float]:
        """ボルツマン分布"""
        xs = [x ** (1 / self.temperature) for x in xs]
        print(type([x / sum(xs) for x in xs]))
        return [x / sum(xs) for x in xs]

    def get_scores(self, model: Model) -> List[float]:
        """スコアの取得"""
        # 現在の局面のノードの作成
        root_node = Node(model=model, state=state, p=0, expand_base=10)
        # 複数回の評価の実行
        for _ in range(PV_EVALUATE_COUNT):
            root_node.evaluate()

        # 合法手の確率分布
        scores = nodes_to_scores(root_node.child_nodes)
        if self.temperature == 0:  # 最大値のみ1
            action = np.argmax(scores)
            scores = np.zeros(len(scores))
            scores[action] = 1
        else:  # ボルツマン分布でバラつき付加
            scores = self.boltzman(scores)
        return scores

    def get_action(self):
        """行動選択"""
        @watch.watch
        def get_action(state: State, model: Model):
            scores = self.get_scores(model)
            return np.random.choice(state.legal_actions(), p=scores)
        return get_action


# 動作確認
if __name__ == '__main__':
    # モデルの読み込み
    path = sorted(Path(f'./model/{SQUARE}x{SQUARE}/').glob('*.h5'))[-1]
    model = load_model(str(path))
    # 状態の生成
    state = State()
    # モンテカルロ木探索で行動取得を行う関数の生成
    mcts = MCTS(temperature=1.0)
    next_action = mcts.get_action()

    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break
        # 行動の取得
        action = next_action(state, model)
        # 次の状態の取得
        state = state.next(action)
        # 文字列表示
        print(state)
