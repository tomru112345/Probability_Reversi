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

# ターンの最大数
MAX_TURNS = 60

WIDTH = 520
HEIGHT = 520

# １マスの大きさ
SQUARE = 50