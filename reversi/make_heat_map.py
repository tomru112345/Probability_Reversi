# ====================
# ヒートマップの作成
# ====================

# パッケージのインポート
from game import State
# from cppState import State
from pv_mcts import pv_mcts_scores
import settings
from settings import SQUARE, default_ratio_box, p, file1
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

# AIのベストプレイヤーのモデルの読み込み
model = load_model(file1)

first_optimal = False
if first_optimal:
    save_path = f'./heat_map/{p}/first_optimal/'
else:
    save_path = f'./heat_map/{p}/first_ai/'
os.makedirs(save_path, exist_ok=True)  # フォルダがない時は生成


def load_optimal_data():
    """最適方策データの読み込み"""
    history_path = Path(f'./optimal_policy/{p}.history')
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def create_color_map(action_list, pi, turn_num, tag):
    # ヒートマップを作成表示
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
    # Loop over data dimensions and create text annotations.
    for i in range(4):
        for j in range(4):
            if 0.3 < turn_policies_np[i, j] < 0.8:
                set_color = "black"
            else:
                set_color = "white"
            plt.text(j, i, format(turn_policies_np[i, j], '.5f'),
                     ha="center", va="center", color=set_color)
    plt.title('{} [{}]'.format(turn_num, tag))
    plt.colorbar()
    plt.savefig(save_path + '{}_{}.png'.format(turn_num, tag))
    plt.close()


def play(V=None, pi=None, board_idx_dict=None, model=model, first_optimal=True):
    np.random.seed(seed=32)
    state = State(default_ratio_box)
    black_win = 0
    white_win = 0
    draw = 0
    # ターン数
    turn_num = 1
    # ゲーム終了までループ
    while True:
        # ゲーム終了時
        if state.is_done():
            if state.is_first_player():
                if state.piece_count(state.get_pieces()) > state.piece_count(state.get_enemy_pieces()):
                    black_win += 1
                elif state.piece_count(state.get_pieces()) < state.piece_count(state.get_enemy_pieces()):
                    white_win += 1
                else:
                    draw += 1
            else:
                if state.piece_count(state.get_pieces()) > state.piece_count(state.get_enemy_pieces()):
                    white_win += 1
                elif state.piece_count(state.get_pieces()) < state.piece_count(state.get_enemy_pieces()):
                    black_win += 1
                else:
                    draw += 1
            break

        pi_s = [
            pi[board_idx_dict[(tuple(state.get_pieces()), tuple(
                state.get_enemy_pieces()), state.get_depth() % 2, state.get_pass_end())]],
            pv_mcts_scores(model, state, 1.0)
        ]

        tags = ['optimal', 'ai']
        if not first_optimal:
            pi_s.reverse()
            tags.reverse()

        if state.is_first_player():
            # if tags[0] == 'ai':
            #     print("ai: {}".format(pi_s[0]))
            #     print("optimal: {}".format(pi_s[1]))
            #     print()
            # else:
            #     print("ai: {}".format(pi_s[1]))
            #     print("optimal: {}".format(pi_s[0]))
            #     print()

            if tags[0] == 'optimal' and turn_num == 1:  # AI との初動を合わせる
                action = state.legal_actions()[1]
                # ヒートマップの作成
                create_color_map(state.legal_actions(), [
                                 0.0, 1.0, 0.0, 0.0], turn_num, tags[0])
            else:
                action = np.random.choice(state.legal_actions(), p=pi_s[0])
                # ヒートマップの作成
                create_color_map(state.legal_actions(),
                                 pi_s[0], turn_num, tags[0])
        else:
            # if tags[1] == 'ai':
            #     print("ai: {}".format(pi_s[1]))
            #     print("optimal: {}".format(pi_s[0]))
            #     print()
            # else:
            #     print("ai: {}".format(pi_s[0]))
            #     print("optimal: {}".format(pi_s[1]))
            #     print()

            action = np.random.choice(state.legal_actions(), p=pi_s[1])
            # ヒートマップの作成
            create_color_map(state.legal_actions(), pi_s[1], turn_num, tags[1])

        # 次の状態の取得
        state = state.next(action, np.random.rand())

        # ターン数の更新
        turn_num += 1

    print(f"{black_win} : {white_win} : {draw}")


if __name__ == '__main__':
    history = load_optimal_data()
    V = history[0]
    pi = history[1]
    board_idx_dict = history[2]
    play(V=V, pi=pi, board_idx_dict=board_idx_dict,
         model=model, first_optimal=first_optimal)
