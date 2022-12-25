# ====================
# 人とAIの対戦
# ====================

# パッケージのインポート
# from game import State
from cppState import State
from pv_mcts import pv_mcts_action
from keras.models import load_model
from pathlib import Path
import tkinter as tk
import pickle
from settings import SQUARE, default_ratio_box
import os
import numpy as np
from datetime import datetime

# tensorflow の warning の設定
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# ベストプレイヤーのモデルの読み込み
model = load_model(f'./model/best.h5')


class GameUI(tk.Frame):
    """ゲームUIの定義"""

    def __init__(self, master=None, model=None, first_ai=False):
        """初期化"""
        tk.Frame.__init__(self, master)
        self.master.title('確率リバーシ')
        self.master.resizable(width=False, height=False)

        # ゲーム状態の生成
        self.state = State(default_ratio_box)

        # PV MCTSで行動選択を行う関数の生成
        self.next_action = pv_mcts_action(model, 0.0)

        # 一つ前の行動選択が何かを保持する
        self.before_action = None
        self.model = model

        self.history = []
        self.human_match_result = [0] * 10

        self.play_cnt = 1

        # キャンバスの生成
        self.c = tk.Canvas(self, width=SQUARE * 100,
                           height=(SQUARE + 1) * 100, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        # AI が先行かどうか
        self.first_ai = first_ai
        if self.first_ai:
            self.turn_of_ai()

        # 描画の更新
        self.on_draw()

    def reset(self):
        """リセット関数"""
        # 一つ前の行動選択が何かを保持する
        self.before_action = None
        # AI が先行かどうか
        if self.first_ai:
            self.turn_of_ai()

    def get_event(self, event):
        return event

    def turn_of_human(self, event):
        """人間のターン"""
        # ゲーム終了時
        self.history.append([self.state.get_pieces(), self.state.get_enemy_pieces(
        ), self.state.get_ratio_box(), self.state.get_depth()])
        if self.state.is_done():
            if self.state.is_lose():
                self.human_match_result[self.play_cnt - 1] = -1
            elif self.state.is_draw():
                self.human_match_result[self.play_cnt - 1] = 0
            else:
                self.human_match_result[self.play_cnt - 1] = 1
            self.state = State(default_ratio_box)
            self.play_cnt += 1
            if self.play_cnt == 6:
                self.first_ai = True
            if self.play_cnt == 11:
                self.write_data()
                exit()
            self.reset()
            self.on_draw()
            return

        # 先手でない時 (人間同士で戦う場合コメントアウトにする)
        if not self.first_ai and not self.state.is_first_player():
            return
        if self.first_ai and self.state.is_first_player():
            return

        # クリック位置を行動に変換
        x = int(event.x/100)
        y = int(event.y/100)
        if x < 0 or (SQUARE - 1) < x or y < 0 or (SQUARE - 1) < y:  # 範囲外
            return
        action = x + y * SQUARE

        # 合法手でない時
        legal_actions = self.state.legal_actions()
        if legal_actions == [SQUARE * SQUARE]:
            action = SQUARE * SQUARE  # パス

        # 前の選択の更新
        self.before_action = action

        if action != (SQUARE * SQUARE) and not (action in legal_actions):
            return

        # 次の状態の取得
        self.state = self.state.next(action, np.random.rand())
        self.on_draw()

        # AIのターン (人間同士で戦う場合コメントアウトにする)
        self.master.after(1, self.turn_of_ai)

    def turn_of_ai(self):
        """AIのターン"""
        self.history.append([self.state.get_pieces(), self.state.get_enemy_pieces(
        ), self.state.get_ratio_box(), self.state.get_depth()])
        # ゲーム終了時
        if self.state.is_done():
            return

        # 行動の取得
        action = self.next_action(self.state)

        # 次の状態の取得
        self.state = self.state.next(action, np.random.rand())

        # 前の選択の更新
        self.before_action = action

        self.on_draw()

    def draw_piece(self, index, first_player):
        """石の描画"""
        x = (index % SQUARE)*100+5
        y = int(index/SQUARE)*100+5
        if first_player:
            self.c.create_oval(x, y, x+100 - 10, y+100 - 10, width=1.0,
                               outline='#000000', fill='#222222')
        else:
            self.c.create_oval(x, y, x+100 - 10, y+100 - 10, width=1.0,
                               outline='#000000', fill='#FFFFFF')

    def draw_result(self):
        x = int((SQUARE * 100) / 2)
        y = int((SQUARE * 100) / 2)
        if self.state.is_first_player():
            black_pieces = self.state.piece_count(self.state.get_pieces())
            white_pieces = self.state.piece_count(
                self.state.get_enemy_pieces())
        else:
            black_pieces = self.state.piece_count(
                self.state.get_enemy_pieces())
            white_pieces = self.state.piece_count(self.state.get_pieces())

        if not self.first_ai:
            if black_pieces > white_pieces:
                self.c.create_text(
                    x, y, text=f'勝利', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")
            elif black_pieces == white_pieces:
                self.c.create_text(
                    x, y, text=f'引き分け', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")
            else:
                self.c.create_text(
                    x, y, text=f'敗北', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")
        else:
            if black_pieces < white_pieces:
                self.c.create_text(
                    x, y, text=f'勝利', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")
            elif black_pieces == white_pieces:
                self.c.create_text(
                    x, y, text=f'引き分け', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")
            else:
                self.c.create_text(
                    x, y, text=f'敗北', fill="#FFFFFF", font=('Yu Gothic UI', 100), anchor="center")

    def draw_ratio(self, index):
        """確率をマス目に表示"""
        x = (index % SQUARE)*100+50
        y = int(index/SQUARE)*100+50
        self.c.create_text(
            x, y, text=str(self.state.get_ratio_box()[index]), fill="#FF0461", font=('Yu Gothic UI', 15), anchor="center")

    def draw_legal_action(self):
        """合法手を表示"""
        legal_action_list = self.state.legal_actions()
        for index in legal_action_list:
            if index != 36:
                x = (index % SQUARE)
                y = int(index/SQUARE)
                self.c.create_rectangle(
                    x * 100, y * 100, (x + 1) * 100, (y + 1) * 100, fill='#FF9900')

    def draw_status(self):
        """現状の石の個数の表示"""
        x = int((SQUARE * 100) / 2)
        y = SQUARE * 100+50
        if self.state.is_first_player():
            black_pieces = self.state.piece_count(self.state.get_pieces())
            white_pieces = self.state.piece_count(
                self.state.get_enemy_pieces())
            self.c.create_rectangle(
                0, SQUARE * 100, SQUARE * 100, (SQUARE + 1) * 100, fill='#222222')
            self.c.create_text(
                x, y, text=f'{black_pieces} : {white_pieces}', fill="#FFFFFF", font=('Yu Gothic UI', 18), anchor="center")
        else:
            black_pieces = self.state.piece_count(
                self.state.get_enemy_pieces())
            white_pieces = self.state.piece_count(self.state.get_pieces())
            self.c.create_rectangle(
                0, SQUARE * 100, SQUARE * 100, (SQUARE + 1) * 100, fill='#FFFFFF')
            self.c.create_text(
                x, y, text=f'{black_pieces} : {white_pieces}', fill="#222222", font=('Yu Gothic UI', 18), anchor="center")

    def draw_turn_player(self):
        """現状の石の個数の表示"""
        x = int((SQUARE * 100) / 2)
        y = SQUARE * 100+50
        turn_player_msg = ["あなた", "AI"]
        if self.first_ai:
            turn_player_msg.reverse()
        if self.state.is_first_player():
            self.c.create_rectangle(
                0, SQUARE * 100, SQUARE * 100, (SQUARE + 1) * 100, fill='#222222')
            self.c.create_text(
                x, y, text=f'{turn_player_msg[0]}', fill="#FFFFFF", font=('Yu Gothic UI', 18), anchor="center")
        else:
            self.c.create_rectangle(
                0, SQUARE * 100, SQUARE * 100, (SQUARE + 1) * 100, fill='#FFFFFF')
            self.c.create_text(
                x, y, text=f'{turn_player_msg[1]}', fill="#222222", font=('Yu Gothic UI', 18), anchor="center")

    def draw_select_icon(self, index):
        """どこを選択したか表示"""
        x = (index % SQUARE)*100+5
        y = int(index/SQUARE)*100+5
        self.c.create_oval(x, y, x+100 - 10, y+100 - 10, width=5.0,
                           outline='#FF0461')

    def push_btn_first_player(self, event):
        self.game_status = 1
        self.first_ai = False
        self.on_draw()

    def on_draw(self):
        """描画の更新"""
        self.c.delete('all')
        self.c.create_rectangle(
            0, 0, SQUARE * 100, SQUARE * 100, width=0.0, fill='#00DD00')

        # 合法手を描画
        self.draw_legal_action()

        for i in range(1, SQUARE + 2):
            self.c.create_line(0, i*100, SQUARE * 100, i*100,
                               width=1.0, fill='#000000')
            self.c.create_line(i*100, 0, i*100, SQUARE * 100,
                               width=1.0, fill='#000000')
        for i in range(SQUARE * SQUARE):
            if self.state.get_pieces()[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.get_enemy_pieces()[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())

            self.draw_ratio(i)

            # 前のターン何を選んだか表示
            if self.before_action == i:
                self.draw_select_icon(i)

        self.draw_turn_player()

    def write_data(self):
        """学習データの保存"""
        now = datetime.now()
        os.makedirs(f'./human_play/', exist_ok=True)  # フォルダがない時は生成
        path = './human_play/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
            now.year, now.month, now.day, now.hour, now.minute, now.second)
        result = [self.history, self.human_match_result]
        with open(path, mode='wb') as f:
            pickle.dump(result, f)


# 動作確認
if __name__ == '__main__':
    # ゲームUIの実行
    f = GameUI(model=model)
    f.pack()
    f.mainloop()
