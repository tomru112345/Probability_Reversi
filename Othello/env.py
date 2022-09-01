from typing import List, Tuple, Literal
import gym
import numpy as np
from gym.spaces import Discrete, Box
from board import Board
import tkinter
import random
import setting
from render import RenderWindow

WIDTH = setting.WIDTH
HEIGHT = setting.HEIGHT


class OthelloEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # 行動空間の定義
        ACTION_NUM = 64
        self.action_space = Discrete(ACTION_NUM)
        self.board = Board()
        observation = self.reset()
        self.observation_space = Box(
            np.float32(np.zeros(observation.shape)), np.float32(np.ones(observation.shape)))

        self.screen = None
        self.done = False

    def step(self, action: int):
        # 手番の表示
        if self.board.CurrentColor == 1:
            movable_y, movable_x = self.board.getMovablePos()
            if not len(movable_x) == 0:
                x, y = self._handle_input(action)
            else:
                x = 1
                y = 9
        else:
            # ランダム相手の手の処理
            movable_y, movable_x = self.board.getMovablePos()
            if not len(movable_x) == 0:
                action_num = random.randint(0, (len(movable_x) - 1))
                x = movable_x[action_num]
                y = movable_y[action_num]
            else:
                x = 1
                y = 9

        if x == 1 and y == 9:  # パスの処理
            self.board.CurrentColor = -self.board.CurrentColor
        if not self.board.move(x, y):  # 手を打つ
            pass

        # 終局判定
        reward = 0
        if self.board.isGameOver():
            self.done = True
            black_num, white_num = self.board.count_stones()
            if black_num > white_num:
                reward = 1
            elif black_num == white_num:
                reward = 0
            else:
                reward = -1

        observation = self.board.MovablePos
        return observation, reward, self.done, {}

    def reset(self) -> np.ndarray:
        self.board.reset()
        observation = self.board.MovablePos
        return observation

    def render(self, mode='human', close=False) -> bool:
        # RawBoardの中身を確認
        if self.screen == None:
            self.screen = tkinter.Tk()
            self.screen.title("確率オセロ")
            self.screen.geometry(f"{WIDTH + 1}x{HEIGHT + 1}")
            # キャンバスエリア
            self.render_class = RenderWindow(self.screen)
            self.render_class.createWidgets()
        # for y in range(10):
        #     for x in range(10):
        #         print('{:^3}'.format(self.board.RawBoard[y, x]), end='')
        #     print()
        # if self.board.CurrentColor == 1:
        #     print("黒の番")
        # else:
        #     print("白の番")
        # print("置く場所を入力 >", end='')
        self.render_class.createBoard(self.board)
        self.screen.update()

    def _handle_input(self, action: int) -> Tuple[int, int]:
        # 手の表現
        # 0 <= action < 65
        # 0 <= action < 63 は盤面に置く
        # 64 はパス
        # 65 はサレンダー
        x = (action % 8 + 1)
        y = (action // 8 + 1)
        return x, y

    # def get_possible_actions(self) -> np.ndarray:
    #     movable_y, movable_x = self.board.getMovablePos()
    #     actions = np.zeros(len(movable_x), dtype=int)
    #     if not len(movable_x) == 0:
    #         for i in range(len(movable_x)):
    #             x = movable_x[i]
    #             y = movable_y[i]
    #             actions[i] = (x - 1) + (y - 1) * 8
    #     return np.array(actions)
