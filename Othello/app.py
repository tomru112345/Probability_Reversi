import tkinter

CANVAS_SIZE = 600
"""キャンバスの横方向・縦方向のサイズ（px）"""
NUM_SQUARE = 8
"""横方向・縦方向のマスの数"""


class App():
    def __init__(self, master):
        self.master = master  # 親ウィジェット
        # １マスのサイズ（px）を計算
        self.square_size = CANVAS_SIZE // NUM_SQUARE
        pass

    def drow_board(self):
        # マスを描画
        for y in range(NUM_SQUARE):
            for x in range(NUM_SQUARE):
                # 長方形の開始・終了座標を計算
                xs = x * self.square_size
                ys = y * self.square_size
                xe = (x + 1) * self.square_size
                ye = (y + 1) * self.square_size

                # 長方形を描画
                tag_name = 'square_' + str(x) + '_' + str(y)
                self.canvas.create_rectangle(
                    xs, ys,
                    xe, ye,
                    tag=tag_name
                )


# スクリプト処理ここから
if __name__ == "__main__":
    app = tkinter.Tk()
    app.title('othello')
    othello = App(app)
    app.mainloop()
