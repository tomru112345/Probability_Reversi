# パッケージのインポート
from game import State, random_action
# from cppState import State
from pv_mcts import pv_mcts_scores
from settings import default_ratio_box, p, file1
import numpy as np
from pathlib import Path
from keras.models import load_model
import pickle
import os

t = ((0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0), (0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0), 0, False)

# tensorflow の warning の設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# GPU メモリを徐々に取得するように設定
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# AIのベストプレイヤーのモデルの読み込み
model = load_model(file1)


def load_data():
    """学習データの読み込み"""
    history_path = Path(f'./optimal_policy/{p}.history')
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def one_game_vs_ai(black_win, white_win, draw, first_optimal=True):
    state = State(default_ratio_box)
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
            action = np.random.choice(state.legal_actions(), p=pi_s[0])
        else:
            action = np.random.choice(state.legal_actions(), p=pi_s[1])

        # 次の状態の取得
        state = state.next(action, np.random.rand())

    return (black_win, white_win, draw)


def play(V=None, pi=None, board_idx_dict=None, n=100, model=None, bisible=False):
    np.random.seed(seed=32)
    if model is not None:
        black_win = 0
        white_win = 0
        draw = 0
        for _ in range(n):
            black_win, white_win, draw = one_game_vs_ai(
                black_win, white_win, draw, first_optimal=True)
            print("\r[optimal vs ai] {} : {} : {}".format(
                black_win, white_win, draw), end='')
        print()

        black_win = 0
        white_win = 0
        draw = 0
        for _ in range(n):
            black_win, white_win, draw = one_game_vs_ai(
                black_win, white_win, draw, first_optimal=False)
            print("\r[ai vs optimal] {} : {} : {}".format(
                black_win, white_win, draw), end='')
        print()


if __name__ == '__main__':
    history = load_data()
    V = history[0]
    pi = history[1]
    board_idx_dict = history[2]
    print(pi[board_idx_dict[t]])
    # play(V=V, pi=pi, board_idx_dict=board_idx_dict,
    #      n=10000, model=model, bisible=False)
