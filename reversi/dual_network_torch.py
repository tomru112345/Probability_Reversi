# import torch
# from torch.nn import Conv2d
# import torch.nn.functional as F
from settings import SQUARE
import os
from keras.layers import Activation, Add, BatchNormalization, Conv2D, Dense, GlobalAveragePooling2D, Input
from keras.models import Model
from keras.regularizers import l2
from keras import backend as K


# パラメータの準備
DN_FILTERS = 128  # 畳み込み層のカーネル数（本家は256）
DN_RESIDUAL_NUM = 16  # 残差ブロックの数（本家は19）
# DN_INPUT_SHAPE = (SQUARE, SQUARE, 2)
DN_INPUT_SHAPE = (SQUARE, SQUARE, 3)  # 入力シェイプ
DN_OUTPUT_SIZE = SQUARE * SQUARE + 1  # 行動数(配置先(6*6)+パス(1))


def conv(filters: int):
    """畳み込み層の作成"""
    # Conv2d(in_channels=1, out_channels=filters, kernel_size=3, padding='same',
    #        bias=False, padding_mode='zeros', device=None, dtype=None)
    """
    convolution(畳み込み)の定義で,第1引数はその入力のチャネル数,第2引数は畳み込み後のチャネル数,第3引数は畳み込みをするための正方形フィルタ(カーネル)の1辺のサイズである.
    最初の畳み込みの例でも言ったが畳み込み後の画像サイズは小さくなるため,畳み込みの例で紹介したlinkで計算しておく.
    """
    return Conv2D(filters=filters, kernel_size=3, padding='same', use_bias=False,
                  kernel_initializer='he_normal', kernel_regularizer=l2(0.0005))


print(conv(1))
