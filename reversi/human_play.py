# ====================
# 人とAIの対戦
# ====================

# パッケージのインポート
from game import State
from pv_mcts import pv_mcts_action
from keras.models import load_model
from pathlib import Path
from threading import Thread
import tkinter as tk
from settings import SQUARE

# ベストプレイヤーのモデルの読み込み
model = load_model(f'./model/{SQUARE}x{SQUARE}/best.h5')

# ゲームUIの定義


class GameUI(tk.Frame):
    # 初期化
    def __init__(self, master=None, model=None):
        tk.Frame.__init__(self, master)
        self.master.title('確率リバーシ')

        # ゲーム状態の生成
        self.state = State()

        # PV MCTSで行動選択を行う関数の生成
        self.next_action = pv_mcts_action(model, 0.0)

        # キャンバスの生成
        self.c = tk.Canvas(self, width=SQUARE * 40,
                           height=SQUARE * 40, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # 描画の更新
        self.on_draw()

    # 人間のターン
    def turn_of_human(self, event):
        # ゲーム終了時
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return

        # 先手でない時
        if not self.state.is_first_player():
            return

        # クリック位置を行動に変換
        x = int(event.x/40)
        y = int(event.y/40)
        if x < 0 or (SQUARE - 1) < x or y < 0 or (SQUARE - 1) < y:  # 範囲外
            return
        action = x + y * SQUARE

        # 合法手でない時
        legal_actions = self.state.legal_actions()
        if legal_actions == [SQUARE * SQUARE]:
            # action = 36  # パス
            action = SQUARE * SQUARE
        if action != (SQUARE * SQUARE) and not (action in legal_actions):
            return

        # 次の状態の取得
        self.state = self.state.next(action)
        self.on_draw()

        # AIのターン
        self.master.after(1, self.turn_of_ai)

    # AIのターン
    def turn_of_ai(self):
        # ゲーム終了時
        if self.state.is_done():
            return

        # 行動の取得
        action = self.next_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action)
        self.on_draw()

    # 石の描画
    def draw_piece(self, index, first_player):
        x = (index % SQUARE)*40+5
        y = int(index/SQUARE)*40+5
        if first_player:
            self.c.create_oval(x, y, x+30, y+30, width=1.0,
                               outline='#000000', fill='#222222')
        else:
            self.c.create_oval(x, y, x+30, y+30, width=1.0,
                               outline='#000000', fill='#FFFFFF')

    # 描画の更新
    def on_draw(self):
        self.c.delete('all')
        self.c.create_rectangle(
            0, 0, SQUARE * 40, SQUARE * 40, width=0.0, fill='#00DD00')
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


# ゲームUIの実行
f = GameUI(model=model)
f.pack()
f.mainloop()
