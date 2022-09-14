# ====================
# パラメータ更新部
# ====================

# パッケージのインポート
from dual_network import DN_INPUT_SHAPE
from keras.callbacks import LearningRateScheduler, LambdaCallback
from keras.models import load_model
from keras import backend as K
from pathlib import Path
import numpy as np
import pickle
from settings import SQUARE
import os
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
# パラメータの準備
RN_EPOCHS = 100  # 学習回数


def load_data():
    """学習データの読み込み"""
    history_path = sorted(
        Path(f'./data/{SQUARE}x{SQUARE}/').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def train_network():
    """デュアルネットワークの学習"""
    # 学習データの読み込み
    history = load_data()
    xs, y_policies, y_values = zip(*history)

    # 学習のための入力データのシェイプの変換
    a, b, c = DN_INPUT_SHAPE
    xs = np.array(xs)
    xs = xs.reshape(len(xs), c, a, b).transpose(0, 2, 3, 1)
    y_policies = np.array(y_policies)
    y_values = np.array(y_values)

    # ベストプレイヤーのモデルの読み込み
    model = load_model(f'./model/{SQUARE}x{SQUARE}/best.h5')

    # モデルのコンパイル
    model.compile(loss=['categorical_crossentropy', 'mse'], optimizer='adam')

    # 学習率
    def step_decay(epoch):
        x = 0.001
        if epoch >= 50:
            x = 0.0005
        if epoch >= 80:
            x = 0.00025
        return x
    lr_decay = LearningRateScheduler(step_decay)

    # 出力
    print_callback = LambdaCallback(
        on_epoch_begin=lambda epoch, logs:
        print('\rTrain {}/{}'.format(epoch + 1, RN_EPOCHS), end=''))

    # 学習の実行
    model.fit(xs, [y_policies, y_values], batch_size=128, epochs=RN_EPOCHS,
              verbose=0, callbacks=[lr_decay, print_callback])
    print('')

    # 最新プレイヤーのモデルの保存
    model.save(f'./model/{SQUARE}x{SQUARE}/latest.h5')

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == '__main__':
    train_network()
