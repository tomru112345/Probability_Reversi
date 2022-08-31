from typing import Tuple, Literal
import gym
import numpy as np
from gym.spaces import Discrete, Box
from board import Board


class Env(gym.Env):
    def __init__(self):
        super().__init__()

        # 行動空間の定義
        # ACTION_NUM = 66
        # self.action_space = Discrete(ACTION_NUM)
        # observation = self.reset()
        # self.observation_space = Box(
        #     np.zeros(observation.shape), np.ones(observation.shape))
        self.board = Board()

        self.done = False

    def step(self, action):
        # 手番の表示
        if self.board.CurrentColor == 1:
            print('黒の番です:', end="")
        else:
            print('白の番です:', end="")

        x, y = self._handle_input(action)
        # 手を打つ
        if not self.board.move(x, y):
            print('そこには置けません')

        # 終局判定
        if self.board.isGameOver():
            self.done = True

        return self.done

    def render(self,  mode: Literal["human", "rgb_array", "ansi"] = "human"):
        # RawBoardの中身を確認
        for y in range(10):
            for x in range(10):
                print('{:^3}'.format(self.board.RawBoard[y, x]), end='')
            print()
        pass

    def _handle_input(self, action: int) -> int:
        # 手の表現
        # 0 <= action < 66
        # 0 <= action < 63 は盤面に置く
        # 64 はパス
        # 65 はサレンダー
        x = action % 8
        y = action / 8
        return x, y
