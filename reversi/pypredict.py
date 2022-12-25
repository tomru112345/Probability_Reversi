# パッケージのインポート
from dual_network import DN_INPUT_SHAPE
import numpy as np


def predict(model, state):
    """推論"""
    # 推論のための入力データのシェイプの変換
    a, b, c = DN_INPUT_SHAPE
    x = np.array(
        [state.get_pieces(), state.get_enemy_pieces(), state.get_ratio_box()])
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c)

    # 推論
    y = model.predict(x=x, batch_size=1)

    # 方策の取得
    policies: list[int] = y[0][0][list(state.legal_actions())]  # 合法手のみ
    policies /= sum(policies) if sum(policies) else 1  # 合計1の確率分布に変換

    # 価値の取得
    value: int = y[1][0][0]
    return policies, value
