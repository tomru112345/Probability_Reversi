import tkinter
import tkinter.messagebox
import setting
from board import Board

WIDTH = setting.WIDTH
HEIGHT = setting.HEIGHT

SQUARE = setting.SQUARE
BOARD_SIZE = setting.BOARD_SIZE
# 色の設定
BOARD_COLOR = 'green'  # 盤面の背景色
YOUR_COLOR = 'black'  # あなたの石の色
COM_COLOR = 'white'  # 相手の石の色
PLACABLE_COLOR = 'yellow'  # 次に石を置ける場所を示す色


class RenderWindow():
    def __init__(self, master: tkinter.Tk):
        super().__init__()
        self.master = master
        self.master.resizable(0, 0)

    def createWidgets(self):
        '''ウィジェットを作成・配置する'''

        # キャンバスの作成
        self.canvas = tkinter.Canvas(
            self.master,
            bg="black",
            width=WIDTH+1,  # +1は枠線描画のため
            height=HEIGHT+1,  # +1は枠線描画のため
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

    def createBoard(self, board: Board) -> None:
        '''ボードの描画'''
        self.canvas.delete("all")

        # マスを描画
        for y in range(BOARD_SIZE + 2):
            for x in range(BOARD_SIZE + 2):
                # 長方形の開始・終了座標を計算
                xs = x * SQUARE
                ys = y * SQUARE
                xe = (x + 1) * SQUARE
                ye = (y + 1) * SQUARE
                # 長方形を描画
                if x == 0 or y == 0 or x == BOARD_SIZE + 1 or y == BOARD_SIZE + 1:
                    if board.CurrentColor > 0:
                        _color = "black"
                    else:
                        _color = "white"
                    outline_color = "black"
                else:
                    _color = "green"
                    outline_color = "black"
                tag_name = 'square_' + str(x) + '_' + str(y)
                self.canvas.create_rectangle(
                    xs, ys,
                    xe, ye,
                    tag=tag_name,
                    fill=_color,
                    outline=outline_color
                )

        movable_y, movable_x = board.getMovablePos()
        for i in range(len(movable_x)):
            x = movable_x[i]
            y = movable_y[i]
            # 長方形の開始・終了座標を計算
            xs = x * SQUARE
            ys = y * SQUARE
            xe = (x + 1) * SQUARE
            ye = (y + 1) * SQUARE
            _color = "yellow"
            outline_color = "black"
            tag_name = 'square_' + str(x) + '_' + str(y)
            self.canvas.create_rectangle(
                xs, ys,
                xe, ye,
                tag=tag_name,
                fill=_color,
                outline=outline_color
            )
            text = self.canvas.create_text(
                (xe+xs)/2, (ye+ys)/2,  # 中心の位置
                text=f"{(x - 1) + (y - 1)* 8}",  # 文字
            )

        for y in range(10):
            for x in range(10):
                # (x,y)のマスの中心座標を計算
                center_x = (x + 0.5) * SQUARE
                center_y = (y + 0.5) * SQUARE
                xs = center_x - (SQUARE * 0.8) // 2
                ys = center_y - (SQUARE * 0.8) // 2
                xe = center_x + (SQUARE * 0.8) // 2
                ye = center_y + (SQUARE * 0.8) // 2
                tag_name = 'disk_' + str(x) + '_' + str(y)
                if board.RawBoard[y, x] == 1:
                    _color = "black"
                    outline_color = "black"
                    self.canvas.create_oval(
                        xs, ys,
                        xe, ye,
                        fill=_color,
                        outline=outline_color,
                        tag=tag_name
                    )
                elif board.RawBoard[y, x] == -1:
                    _color = "white"
                    outline_color = "black"
                    self.canvas.create_oval(
                        xs, ys,
                        xe, ye,
                        fill=_color,
                        outline=outline_color,
                        tag=tag_name
                    )
