# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート
from dual_network import dual_network
from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network
import os

# tensorflow の warning の設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# GPU メモリを徐々に取得するように設定
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# デュアルネットワークの作成
dual_network()

for i in range(200):
    print('Train', i, '====================')

    # セルフプレイ部
    self_play()

    # パラメータ更新部
    train_network()

    # 新パラメータ評価部
    evaluate_network()
