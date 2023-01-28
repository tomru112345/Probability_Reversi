# ====================
# ヒートマップの作成
# ====================

# パッケージのインポート
from game import State
# from cppState import State
from pv_mcts import pv_mcts_scores
import settings
from settings import SQUARE, default_ratio_box
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

is_optimal = False
save_path = f'./heat_map/'
os.makedirs(save_path, exist_ok=True)  # フォルダがない時は生成

m = 600


def load_optimal_data(p):
    """最適方策データの読み込み"""
    history_path = Path(f'./optimal_policy/{p}.history')
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


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
        plt.title('{} {}'.format(p, m), fontsize=20)
        plt.colorbar()
        plt.savefig(save_path + '{}_{}.png'.format(m, p))
        plt.close()


def play(V, pi, board_idx_dict, model, p, is_optimal=True):
    np.random.seed(seed=32)
    state = State(pieces=[0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0,
                  0, 0, 0], enemy_pieces=[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], ratio_box=default_ratio_box, depth=1)
    pi_s = [pi[board_idx_dict[(tuple(state.get_pieces()), tuple(state.get_enemy_pieces(
    )), state.get_depth() % 2, state.get_pass_end())]], pv_mcts_scores(model, state, 1.0)]
    tags = ['optimal', 'ai']
    if not is_optimal:
        pi_s.reverse()
        tags.reverse()
    print(state)
    # ヒートマップの作成
    create_color_map(state.legal_actions(), pi_s[0], tags[0], p)


if __name__ == '__main__':
    for p in range(1, 11):
        print(f"# {p}")
        history = load_optimal_data(p)
        V = history[0]
        pi = history[1]
        board_idx_dict = history[2]
        model = load_model(f'./model/{m}/best_{p}.h5')
        play(V=V, pi=pi, board_idx_dict=board_idx_dict,
             model=model, p=p, is_optimal=is_optimal)
