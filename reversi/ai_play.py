# ====================
# AIとAIの対戦
# ====================

# パッケージのインポート
from game import State
from pv_mcts import pv_mcts_action
from keras.models import load_model
from pathlib import Path
from threading import Thread
import tkinter as tk
from settings import SQUARE
import time

# それぞれのAIのベストプレイヤーのモデルの読み込み
model_1 = load_model(f'./model/{SQUARE}x{SQUARE}/best.h5')
model_2 = load_model(f'./model/{SQUARE}x{SQUARE}/best.h5')


class GameUI(tk.Frame):
    """ゲームUIの定義"""

    def __init__(self, master=None, model_1=None, model_2=None):
        """初期化"""
        tk.Frame.__init__(self, master)
        self.master.title('確率リバーシ')

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

        # 勝利数
        self.black_win_cnt = 0
        self.white_win_cnt = 0

        # キャンバスの生成
        self.c = tk.Canvas(self, width=SQUARE * 40,
                           height=(SQUARE + 1) * 40, highlightthickness=0)
        # self.c.bind('<Button-1>', self.click_start)
        self.c.pack()

        # 描画の更新
        self.on_draw()
        self.reset()

    def reset(self):
        """リセット関数"""
        # 一つ前の行動選択が何かを保持する
        self.before_action = None

        # 百回対戦させる
        if self.game_cnt == 100:
            print(f"黒: {self.black_win_cnt}, 白: {self.white_win_cnt}")
            return

        self.game_cnt += 1
        self.turn_of_ai_1()

    def get_event(self, event):
        return event

    def preview_result(self):
        if self.black_pieces > self.white_pieces:
            self.black_win_cnt += 1
        elif self.black_pieces < self.white_pieces:
            self.white_win_cnt += 1

    def click_start(self, event):
        self.turn_of_ai_1()

    def turn_of_ai_1(self):
        """AIのターン"""
        # ゲーム終了時
        if self.state.is_done():
            self.state = State()
            self.preview_result()
            # time.sleep(5)
            self.reset()
            self.on_draw()
            return

        # 行動の取得
        action = self.current_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action)

        # 前の選択の更新
        self.before_action = action
        self.on_draw()

        # AIのターン (人間同士で戦う場合コメントアウトにする)
        self.master.after(1, self.turn_of_ai_2)

    def turn_of_ai_2(self):
        """AIのターン"""
        # ゲーム終了時
        if self.state.is_done():
            self.master.after(1, self.turn_of_ai_1)
            return

        # 行動の取得
        action = self.next_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action)

        # 前の選択の更新
        self.before_action = action
        self.on_draw()

        self.master.after(1, self.turn_of_ai_1)

    def draw_piece(self, index, first_player):
        """石の描画"""
        x = (index % SQUARE)*40+5
        y = int(index/SQUARE)*40+5
        if first_player:
            self.c.create_oval(x, y, x+30, y+30, width=1.0,
                               outline='#000000', fill='#222222')
        else:
            self.c.create_oval(x, y, x+30, y+30, width=1.0,
                               outline='#000000', fill='#FFFFFF')

    def draw_ratio(self, index):
        """確率をマス目に表示"""
        x = (index % SQUARE)*40+20
        y = int(index/SQUARE)*40+20
        self.c.create_text(
            x, y, text=str(self.state.ratio_box[index]), fill="#FF0461", font=('Yu Gothic UI', 18), anchor="center")

    def draw_legal_action(self):
        """合法手を表示"""
        legal_action_list = self.state.legal_actions()
        for index in legal_action_list:
            if index != 36:
                x = (index % SQUARE)
                y = int(index/SQUARE)
                self.c.create_rectangle(
                    x * 40, y * 40, (x + 1) * 40, (y + 1) * 40, fill='#FF9900')

    def draw_status(self):
        """現状の石の個数の表示"""
        x = int((SQUARE * 40) / 2)
        y = SQUARE * 40+20
        if self.state.is_first_player():
            black_pieces = self.state.piece_count(self.state.pieces)
            white_pieces = self.state.piece_count(self.state.enemy_pieces)
            self.c.create_rectangle(
                0, SQUARE * 40, SQUARE * 40, (SQUARE + 1) * 40, fill='#222222')
            self.c.create_text(
                x, y, text=f'{black_pieces} vs {white_pieces}', fill="#FFFFFF", font=('Yu Gothic UI', 18), anchor="center")
        else:
            black_pieces = self.state.piece_count(self.state.enemy_pieces)
            white_pieces = self.state.piece_count(self.state.pieces)
            self.c.create_rectangle(
                0, SQUARE * 40, SQUARE * 40, (SQUARE + 1) * 40, fill='#FFFFFF')
            self.c.create_text(
                x, y, text=f'{black_pieces} vs {white_pieces}', fill="#222222", font=('Yu Gothic UI', 18), anchor="center")
        self.black_pieces = black_pieces
        self.white_pieces = white_pieces

    def draw_select_icon(self, index):
        """どこを選択したか表示"""
        x = (index % SQUARE)*40+5
        y = int(index/SQUARE)*40+5
        self.c.create_oval(x, y, x+30, y+30, width=5.0,
                           outline='#FF0461')

    def on_draw(self):
        """描画の更新"""
        self.c.delete('all')
        self.c.create_rectangle(
            0, 0, SQUARE * 40, SQUARE * 40, width=0.0, fill='#00DD00')

        # 合法手を描画
        self.draw_legal_action()

        for i in range(1, SQUARE + 2):
            self.c.create_line(0, i*40, SQUARE * 40, i*40,
                               width=1.0, fill='#000000')
            self.c.create_line(i*40, 0, i*40, SQUARE * 40,
                               width=1.0, fill='#000000')
        for i in range(SQUARE * SQUARE):
            if self.state.pieces[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())

            self.draw_ratio(i)

            # 前のターン何を選んだか表示
            if self.before_action == i:
                self.draw_select_icon(i)

        self.draw_status()


# 動作確認
if __name__ == '__main__':
    # ゲームUIの実行
    f = GameUI(model_1=model_1, model_2=model_2)
    f.pack()
    f.mainloop()
