import numpy as np

# マスの状態
EMPTY = 0  # 空きマス
WHITE = -1  # 白石
BLACK = 1  # 黒石
WALL = 2  # 壁

# ボードのサイズ
BOARD_SIZE = 8

# 方向(2進数)
NONE = 0
LEFT = 2**0  # =1
UPPER_LEFT = 2**1  # =2
UPPER = 2**2  # =4
UPPER_RIGHT = 2**3  # =8
RIGHT = 2**4  # =16
LOWER_RIGHT = 2**5  # =32
LOWER = 2**6  # =64
LOWER_LEFT = 2**7  # =128


MAX_TURNS = 60

"""
ボードの表現
"""


class Board:

    def __init__(self):

        # 全マスを空きマスに設定
        self.RawBoard = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)

        # 置ける場所と石が返る方向
        self.MovablePos = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)
        self.MovableDir = np.zeros((BOARD_SIZE + 2, BOARD_SIZE + 2), dtype=int)

        # 壁の設定
        self.RawBoard[0, :] = WALL
        self.RawBoard[:, 0] = WALL
        self.RawBoard[BOARD_SIZE + 1, :] = WALL
        self.RawBoard[:, BOARD_SIZE + 1] = WALL

        # 初期配置
        self.RawBoard[4, 4] = WHITE
        self.RawBoard[5, 5] = WHITE
        self.RawBoard[4, 5] = BLACK
        self.RawBoard[5, 4] = BLACK

        # 手番
        self.Turns = 0

        # 現在の手番の色
        self.CurrentColor = BLACK

        # MovablePosとMovableDirを初期化
        self.initMovable()

    """
    どの方向に石が裏返るかをチェック
    """

    def checkMobility(self, x, y, color):

        # 注目しているマスの裏返せる方向の情報が入る
        dir = 0

        # 既に石がある場合はダメ
        if(self.RawBoard[y, x] != EMPTY):
            return dir

        # 左
        if(self.RawBoard[y, x - 1] == - color):  # 直上に相手の石があるか

            x_tmp = x - 2
            y_tmp = y

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp -= 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | LEFT

        # 左上
        if(self.RawBoard[y - 1, x - 1] == - color):  # 直上に相手の石があるか

            x_tmp = x - 2
            y_tmp = y - 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp -= 1
                y_tmp -= 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | UPPER_LEFT

        # 上
        if(self.RawBoard[y - 1, x] == - color):  # 直上に相手の石があるか

            x_tmp = x
            y_tmp = y - 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                y_tmp -= 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | UPPER

        # 右上
        if(self.RawBoard[y - 1, x + 1] == - color):  # 直上に相手の石があるか

            x_tmp = x + 2
            y_tmp = y - 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp += 1
                y_tmp -= 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | UPPER_RIGHT

        # 右
        if(self.RawBoard[y, x + 1] == - color):  # 直上に相手の石があるか

            x_tmp = x + 2
            y_tmp = y

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp += 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | RIGHT

        # 右下
        if(self.RawBoard[y + 1, x + 1] == - color):  # 直上に相手の石があるか

            x_tmp = x + 2
            y_tmp = y + 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp += 1
                y_tmp += 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | LOWER_RIGHT

        # 下
        if(self.RawBoard[y + 1, x] == - color):  # 直上に相手の石があるか

            x_tmp = x
            y_tmp = y + 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                y_tmp += 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | LOWER

        # 左下
        if(self.RawBoard[y + 1, x - 1] == - color):  # 直上に相手の石があるか

            x_tmp = x - 2
            y_tmp = y + 2

            # 相手の石が続いているだけループ
            while self.RawBoard[y_tmp, x_tmp] == - color:
                x_tmp -= 1
                y_tmp += 1

            # 相手の石を挟んで自分の石があればdirを更新
            if self.RawBoard[y_tmp, x_tmp] == color:
                dir = dir | LOWER_LEFT

        return dir

    """
    石を置くことによる盤面の変化をボードに反映
    """

    def flipDiscs(self, x: int, y: int) -> bool:

        # 石を置く
        self.RawBoard[y, x] = self.CurrentColor

        # 石を裏返す
        # MovableDirの(y, x)座標をdirに代入
        dir = self.MovableDir[y, x]

        # 左
        if dir & LEFT:  # AND演算子

            x_tmp = x - 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y, x_tmp] = self.CurrentColor

                # さらに1マス左に進めてループを回す
                x_tmp -= 1

        # 左上
        if dir & UPPER_LEFT:  # AND演算子

            x_tmp = x - 1
            y_tmp = y - 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x_tmp] = self.CurrentColor

                # さらに1マス左上に進めてループを回す
                x_tmp -= 1
                y_tmp -= 1

        # 上
        if dir & UPPER:  # AND演算子

            y_tmp = y - 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x] = self.CurrentColor

                # さらに1マス上に進めてループを回す
                y_tmp -= 1

        # 右上
        if dir & UPPER_RIGHT:  # AND演算子

            x_tmp = x + 1
            y_tmp = y - 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x_tmp] = self.CurrentColor

                # さらに1マス右上に進めてループを回す
                x_tmp += 1
                y_tmp -= 1

        # 右
        if dir & RIGHT:  # AND演算子

            x_tmp = x + 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y, x_tmp] = self.CurrentColor

                # さらに1マス右に進めてループを回す
                x_tmp += 1

        # 右下
        if dir & LOWER_RIGHT:  # AND演算子

            x_tmp = x + 1
            y_tmp = y + 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x_tmp] = self.CurrentColor

                # さらに1マス右下に進めてループを回す
                x_tmp += 1
                y_tmp += 1

        # 下
        print(dir, LOWER)
        if dir & LOWER:  # AND演算子

            y_tmp = y + 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x] = self.CurrentColor

                # さらに1マス下に進めてループを回す
                y_tmp += 1

        # 左下
        if dir & LOWER_LEFT:  # AND演算子

            x_tmp = x - 1
            y_tmp = y + 1

            # 相手の石がある限りループが回る
            while self.RawBoard[y_tmp, x_tmp] == - self.CurrentColor:

                # 相手の石があるマスを自分の石の色に塗り替えている
                self.RawBoard[y_tmp, x_tmp] = self.CurrentColor

                # さらに1マス左下に進めてループを回す
                x_tmp -= 1
                y_tmp += 1

    """
    石を置く
    """

    def move(self, x: int, y: int) -> bool:

        # 置く位置が正しいかどうかをチェック
        if x < 1 or BOARD_SIZE < x:
            return False
        if y < 1 or BOARD_SIZE < y:
            return False
        if self.MovablePos[y, x] == 0:
            return False

        # 石を裏返す
        self.flipDiscs(x, y)

        # 手番を進める
        self.Turns += 1

        # 手番を交代する
        self.CurrentColor = - self.CurrentColor

        # MovablePosとMovableDirの更新
        self.initMovable()

        return True

    """
    MovablePosとMovableDirの更新
    """

    def initMovable(self):

        # MovablePosの初期化（すべてFalseにする）
        self.MovablePos[:, :] = False

        # すべてのマス（壁を除く）に対してループ
        for y in range(1, BOARD_SIZE + 1):
            for x in range(1, BOARD_SIZE + 1):

                # checkMobility関数の実行
                dir = self.checkMobility(x, y, self.CurrentColor)

                # 各マスのMovableDirにそれぞれのdirを代入
                self.MovableDir[y, x] = dir

                # dirが0でないならMovablePosにTrueを代入
                if dir != 0:
                    self.MovablePos[y, x] = True

    def isGameOver(self) -> bool:
        """終局判定"""

        # 60手に達していたらゲーム終了
        if self.Turns >= MAX_TURNS:
            return True

        # (現在の手番)打てる手がある場合はゲームを終了しない
        if self.MovablePos[:, :].any():
            return False

        # (相手の手番)打てる手がある場合はゲームを終了しない
        for x in range(1, BOARD_SIZE + 1):
            for y in range(1, BOARD_SIZE + 1):

                # 置ける場所が1つでもある場合はゲーム終了ではない
                if self.checkMobility(x, y, - self.CurrentColor) != 0:
                    return False

        # ここまでたどり着いたらゲームは終わっている
        return True
