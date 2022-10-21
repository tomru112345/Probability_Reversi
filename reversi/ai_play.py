# ====================
# AIとAIの対戦
# ====================
# パッケージのインポート
from game import State
from pv_mcts import pv_mcts_action
from datetime import datetime
import settings
import os
from keras.models import load_model

# それぞれのAIのベストプレイヤーのモデルの読み込み
model_1 = load_model(settings.file1)
model_2 = load_model(settings.file2)


class AIBattle():
    """ゲームUIの定義"""

    def __init__(self, model_1=None, model_2=None):
        """初期化"""

        # ゲーム状態の生成
        self.state = State()

        # PV MCTSで行動選択を行う関数の生成
        self.current_action = pv_mcts_action(model_1, 0.0)
        self.next_action = pv_mcts_action(model_2, 0.0)

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

        self.reset()

    def reset(self):
        """リセット関数"""
        # 一つ前の行動選択が何かを保持する
        self.before_action = None
        self.calculate_status()
        # 百回対戦させる
        if self.game_cnt == 100:
            print()
            print(f"黒: {self.black_win_cnt}, 白: {self.white_win_cnt}")
            self.write_data()
            return

        self.game_cnt += 1
        # ログ出力
        print('\r[Play_AIvsAI {}/{}] <黒: {}勝, 白: {}勝>'.format(self.game_cnt,
              100, self.black_win_cnt, self.white_win_cnt), end='')
        self.one_turn()

    def get_event(self, event):
        return event

    def preview_result(self):
        if self.black_pieces > self.white_pieces:
            self.black_win_cnt += 1
        elif self.black_pieces < self.white_pieces:
            self.white_win_cnt += 1

    def one_turn(self):
        self.game_fin = False
        while self.game_fin == False:
            self.turn_clean()
            self.turn_of_ai_1()
            self.turn_of_ai_2()

    def turn_of_ai_1(self):
        """AIのターン"""
        # ゲーム終了時
        if self.state.is_done():
            return

        # 行動の取得
        action = self.current_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action)

        # 前の選択の更新
        self.before_action = action
        self.calculate_status()

    def turn_of_ai_2(self):
        """AIのターン"""
        # ゲーム終了時
        if self.state.is_done():
            return

        # 行動の取得
        action = self.next_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action)

        # 前の選択の更新
        self.before_action = action
        self.calculate_status()

    def turn_clean(self):
        # ゲーム終了時
        if self.state.is_done():
            self.state = State()
            self.preview_result()
            self.reset()
            self.calculate_status()
            self.game_fin = True
            return

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
    # ゲームUIの実行
    game = AIBattle(model_1=model_1, model_2=model_2)
