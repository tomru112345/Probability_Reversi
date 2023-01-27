import cv2
import os
from game import State
import tkinter as tk
from settings import SQUARE, default_ratio_box, p
import numpy as np
import pickle
from pathlib import Path


def load_data():
    """学習データの読み込み"""
    history_path = Path(f'./optimal_policy/{p}.history')
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])


def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)


def combine_images():
    os.makedirs('images', exist_ok=True)  # フォルダがない時は生成
    im = []
    for i in range(1, 11):
        im = []
        im.append(cv2.resize(
            cv2.imread(f'./images/board_{i}.png'), dsize=(1000, 1000)))
        im.append(cv2.resize(
            cv2.imread(f'./heat_map/{i}_ai.png'), dsize=(0, 0), fx=0.5, fy=0.5))
        # im = np.array(im)
        im_h_resize = hconcat_resize_min(im)
        cv2.imwrite(f'images/heat_map_{i}.png', im_h_resize)


def combine_heat_maps():
    os.makedirs('images', exist_ok=True)  # フォルダがない時は生成
    images = []
    cnt = 1
    for j in range(1, 11):
        if j % 2 == 1:
            im = []
            im.append(cv2.resize(cv2.imread(
                f'./images/heat_map_{j}.png'), dsize=(0, 0), fx=1.0, fy=1.0))
            im.append(cv2.resize(cv2.imread(
                f'./images/heat_map_{j+1}.png'), dsize=(0, 0), fx=1.0, fy=1.0))
            images.append(im)
            im_h_resize = concat_tile(images)
            cv2.imwrite(f'images/heat_maps_{cnt}.png', im_h_resize)
            cnt += 1
            images = []


class GameUI(tk.Frame):
    """ゲームUIの定義"""

    def __init__(self, master=None):
        """初期化"""
        tk.Frame.__init__(self, master)
        self.master.title('確率リバーシ')
        self.master.resizable(width=False, height=False)

        # ゲーム状態の生成
        self.state = State(
            pieces=[0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0,
                    0, 0, 0],
            enemy_pieces=[0, 0, 0, 0, 0, 1,
                          0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            ratio_box=default_ratio_box,
            depth=1
        )
        history = load_data()
        V = history[0]
        pi = history[1]
        board_idx_dict = history[2]
        for i in range(len(pi[board_idx_dict[(tuple(self.state.pieces), tuple(self.state.enemy_pieces), self.state.depth % 2, self.state.pass_end)]])):
            if pi[board_idx_dict[(tuple(self.state.pieces), tuple(self.state.enemy_pieces), self.state.depth % 2, self.state.pass_end)]][i] == 1:
                self.action = self.state.legal_actions()[i]

        print(self.action)
        # キャンバスの生成
        self.c = tk.Canvas(self, width=6 * 100,
                           height=6 * 100, highlightthickness=0)
        self.c.pack()
        # 描画の更新
        self.on_draw()

    def draw_piece(self, index, first_player):
        """石の描画"""
        x = (index % SQUARE)*100+5 + 100
        y = int(index/SQUARE)*100+5 + 100
        if first_player:
            self.c.create_oval(x, y, x+100 - 10, y+100 - 10, width=1.0,
                               outline='#000000', fill='#222222')
        else:
            self.c.create_oval(x, y, x+100 - 10, y+100 - 10, width=1.0,
                               outline='#000000', fill='#FFFFFF')

    def draw_ratio(self, index):
        """確率をマス目に表示"""
        x = (index % SQUARE)*100+50 + 100
        y = int(index/SQUARE)*100+50 + 100
        self.c.create_text(
            x, y, text=str(self.state.get_ratio_box()[index]), fill="#FF0461", font=('Yu Gothic UI', 50, 'bold'), anchor="center")

    def draw_select_icon(self):
        """どこを選択したか表示"""
        x = (self.action % SQUARE)*100+5
        y = int(self.action/SQUARE)*100+5
        self.c.create_oval(x + 100, y + 100, x + 100+100 - 10, y + 100+100 - 10, width=5.0,
                           outline='#0000ff')

    def on_draw(self):
        """描画の更新"""
        self.c.delete('all')
        self.c.create_rectangle(
            0 + 100, 0 + 100, SQUARE * 100 + 100, SQUARE * 100 + 100, width=0.0, fill='#00DD00')

        for i in range(0, SQUARE + 2):
            self.c.create_line(0 + 100, i*100 + 100, SQUARE * 100 + 100, i*100 + 100,
                               width=1.0, fill='#000000')
            self.c.create_line(i*100 + 100, 0 + 100, i*100 + 100, SQUARE * 100 + 100,
                               width=1.0, fill='#000000')

        for i in range(SQUARE * SQUARE):
            if self.state.get_pieces()[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.get_enemy_pieces()[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())

            self.draw_ratio(i)
            # 最適方策を表示
            # if self.action == i:
            #     self.draw_select_icon()


def main():
    f = GameUI()
    f.pack()
    f.mainloop()


# combine_images()
# combine_heat_maps()
main()
