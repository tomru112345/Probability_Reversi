# ====================
# AIとAIの対戦
# ====================
# パッケージのインポート
# from game import State
from cppState import State
from pv_mcts import pv_mcts_action_policy
from datetime import datetime
import settings
from settings import SQUARE, default_ratio_box
import os
import numpy as np
from keras.models import load_model
import matplotlib as mpl
import matplotlib.pyplot as plt

# GPU メモリを徐々に取得するように設定
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# それぞれのAIのベストプレイヤーのモデルの読み込み
model_1 = load_model(settings.file1)
model_2 = load_model(settings.file2)

EN_TEMPERATURE = 1.0


class AIBattle():
    """AI同士のバトルのクラスの定義"""

    def __init__(self, model_1=None, model_2=None):
        """初期化"""

        # ゲーム状態の生成
        self.state = State(default_ratio_box)

        # PV MCTSで行動選択を行う関数の生成
        self.next_action = pv_mcts_action_policy(model_1, EN_TEMPERATURE) if self.state.is_first_player(
        ) else pv_mcts_action_policy(model_2, EN_TEMPERATURE)

        # ターンの方策
        self.turn_policies = None

        # ターン数
        self.turn_num = 0

        # 保存用グラフ
        # now = datetime.now()
        # self.path = './ai_vs_ai/color_map/{:04}{:02}{:02}{:02}{:02}{:02}/'.format(
        #     now.year, now.month, now.day, now.hour, now.minute, now.second)
        # os.makedirs(self.path, exist_ok=True)  # フォルダがない時は生成
        # 一つ前の行動選択が何かを保持する
        self.before_action = None

        # 駒の数を数える
        self.black_pieces = 2
        self.white_pieces = 2

        # 試合数
        self.game_cnt = 0

        self.game_fin = False

        # 勝利数
        self.black_win_cnt = 0
        self.white_win_cnt = 0

    def start_battle(self):
        """リセット関数"""
        # 一つ前の行動選択が何かを保持する
        self.before_action = None
        self.calculate_status()
        self.game_cnt += 1
        print('\rPlay_AIvsAI {}/{} {}:{}'.format(self.game_cnt,
              1000, self.black_win_cnt, self.white_win_cnt), end='')
        self.one_turn()
        # ログ出力

    def get_event(self, event):
        return event

    def preview_result(self):
        if self.black_pieces > self.white_pieces:
            self.black_win_cnt += 1
        elif self.black_pieces < self.white_pieces:
            self.white_win_cnt += 1

    def one_turn(self):
        """1 つのターンの関数"""
        self.game_fin = False
        self.turn_num = 0
        while self.game_fin == False:
            # ゲーム終了時
            if self.state.is_done():
                self.state = State(default_ratio_box)
                self.preview_result()
                self.calculate_status()
                self.game_fin = True
                return
            self.turn_of_ai()
            # self.create_color_map()
        self.write_data()

    def turn_of_ai(self):
        """AI1のターン"""
        # ゲーム終了時
        if self.state.is_done():
            return

        self.turn_num += 1
        # 行動の取得, ターンの方策の更新
        action, self.turn_policies = self.next_action(self.state)
        # 次の状態の取得
        self.state = self.state.next(action)

        # 前の選択の更新
        self.before_action = action
        self.calculate_status()

    def create_color_map(self):
        # カラーマップを作成表示
        turn_policies_np = np.array(self.turn_policies)
        turn_policies_np = turn_policies_np.reshape([SQUARE, SQUARE])
        plt.figure()
        plt.imshow(turn_policies_np, cmap=plt.cm.jet,
                   interpolation='nearest', vmin=0, vmax=1)
        plt.title('{}'.format(self.turn_num))
        plt.colorbar()
        plt.savefig(self.path + '{}.png'.format(self.turn_num))
        plt.close()

    def calculate_status(self):
        """現状の石の個数の表示"""
        if self.state.is_first_player():
            black_pieces = self.state.piece_count(self.state.pieces)
            white_pieces = self.state.piece_count(self.state.enemy_pieces)
        else:
            black_pieces = self.state.piece_count(self.state.enemy_pieces)
            white_pieces = self.state.piece_count(self.state.pieces)
        self.black_pieces = black_pieces
        self.white_pieces = white_pieces

    def write_data(self):
        """学習データの保存"""
        now = datetime.now()
        os.makedirs(f'./ai_vs_ai/', exist_ok=True)  # フォルダがない時は生成
        path = './ai_vs_ai/{:04}{:02}{:02}{:02}{:02}{:02}.txt'.format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)
        with open(path, mode='w', encoding='utf-8') as f:
            f.write('黒: ' + settings.file1 + '\n')
            f.write('白: ' + settings.file2 + '\n')
            f.write('黒: {}勝, 白: {}勝'.format(
                self.black_win_cnt, self.white_win_cnt))


# 動作確認
if __name__ == '__main__':
    # 実行
    game = AIBattle(model_1=model_1, model_2=model_2)
    for i in range(1000):
        game.start_battle()
