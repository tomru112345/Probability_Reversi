# ====================
# ヒートマップの作成
# ====================

# パッケージのインポート
from game import State
# from cppState import State
from pv_mcts import pv_mcts_scores
import settings
from settings import SQUARE, create_ratiobox_set_value
import os
import numpy as np
from pathlib import Path
import pickle
from keras.models import load_model
import matplotlib as mpl
import matplotlib.pyplot as plt


# tensorflow の warning の設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# GPU メモリを徐々に取得するように設定
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

save_path = f'./heat_map/'
os.makedirs(save_path, exist_ok=True)  # フォルダがない時は生成

m = 600


def create_color_map(action_list, pi, tag, p):
    # ヒートマップを作成表示
    if tag == 'ai':
        heat_map_list = [0.0] * (SQUARE*SQUARE)
        for i in range(SQUARE*SQUARE):
            if i in action_list:
                heat_map_list[i] = pi[action_list.index(i)]
        turn_policies_np = np.array(heat_map_list)
        turn_policies_np = turn_policies_np.reshape([SQUARE, SQUARE])
        plt.figure()
        plt.imshow(turn_policies_np, cmap=plt.cm.jet,
                   interpolation='nearest', vmin=0, vmax=1)
        plt.axis("off")
        for i in range(4):
            for j in range(4):
                if 0.3 < turn_policies_np[i, j] < 0.8:
                    set_color = "black"
                else:
                    set_color = "white"
                plt.text(j, i, format(turn_policies_np[i, j], '.3f'),
                         ha="center", va="center", color=set_color, fontsize=20)
        plt.title('{}'.format(p), fontsize=20)
        plt.colorbar()
        plt.savefig(save_path + '{}_{}.pdf'.format(m, p))
        plt.close()


if __name__ == '__main__':
    for p in range(1, 11):
        print(f"# {p}")
        model = load_model(f'./model/{m}/best_{p}.h5')
        np.random.seed(seed=32)
        state = State(pieces=[0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
                      enemy_pieces=[0, 0, 0, 0, 0, 1,
                                    0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                      ratio_box=create_ratiobox_set_value(p),
                      depth=1)
        print(state)
        # ヒートマップの作成
        create_color_map(state.legal_actions(),
                         pv_mcts_scores(model, state, 1.0), 'ai', p)
        del model
