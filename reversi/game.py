# ====================
# リバーシ
# ====================

# パッケージのインポート
from settings import SQUARE, default_ratio_box
import watch
import numpy as np


class State:
    """ゲーム状態"""

    def __init__(self, pieces=None, enemy_pieces=None, ratio_box=None, depth=0):
        """初期化"""
        # 方向定数
        self.dxy = ((1, 0), (1, 1), (0, 1), (-1, 1),
                    (-1, 0), (-1, -1), (0, -1), (1, -1))

        # 連続パスによる終了
        self.pass_end = False

        # 石の配置
        self.pieces = pieces
        self.enemy_pieces = enemy_pieces
        self.depth = depth

        # 確率用のリスト
        self.ratio_box = ratio_box

        # 石の初期配置
        if pieces == None or enemy_pieces == None:
            self.pieces = [0] * SQUARE * SQUARE
            self.enemy_pieces = [0] * SQUARE * SQUARE

            # 座標の指定用変数
            center_idx = int((SQUARE * SQUARE) / 2)
            balance_idx = int(SQUARE / 2)
            self.pieces[center_idx - balance_idx - 1] = 1
            self.pieces[center_idx + balance_idx] = 1
            self.enemy_pieces[center_idx - balance_idx] = 1
            self.enemy_pieces[center_idx + balance_idx - 1] = 1

            # 確率値の初期化
            self.ratio_box = default_ratio_box

    def get_pieces(self):
        return self.pieces
    
    def get_enemy_pieces(self):
        return self.enemy_pieces

    def get_ratio_box(self):
        return self.ratio_box

    def get_depth(self):
        return self.depth

    def get_pass_end(self):
        return self.pass_end

    def piece_count(self, pieces):
        """石の数の取得"""
        count = 0
        for i in pieces:
            if i == 1:
                count += 1
        return count

    def is_lose(self):
        """負けかどうか"""
        return self.is_done() and self.piece_count(self.pieces) < self.piece_count(self.enemy_pieces)

    def is_draw(self):
        """引き分けかどうか"""
        return self.is_done() and self.piece_count(self.pieces) == self.piece_count(self.enemy_pieces)

    def is_done(self):
        """ゲーム終了かどうか"""
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == (SQUARE * SQUARE) or self.pass_end

    def next(self, action: int, set_ratio: float = 0):
        """次の状態の取得"""
        state = State(self.pieces.copy(),
                      self.enemy_pieces.copy(), self.ratio_box.copy(), self.depth+1)

        if action != (SQUARE * SQUARE):  # パスを選択していないとき
            if (set_ratio * 100) < self.ratio_box[action % SQUARE+int(action/SQUARE)*SQUARE]:
                state.is_legal_action_xy(
                    action % SQUARE, int(action/SQUARE), True, True)
            else:
                state.is_legal_action_xy(
                    action % SQUARE, int(action/SQUARE), True, False)

        w = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = w

        # 2回連続パス判定
        if action == (SQUARE * SQUARE) and state.legal_actions() == [SQUARE * SQUARE]:
            state.pass_end = True
        return state

    def legal_actions(self):
        """合法手のリストの取得"""
        actions = []
        for j in range(0, SQUARE):
            for i in range(0, SQUARE):
                if self.is_legal_action_xy(i, j):
                    actions.append(i+j*SQUARE)
        if len(actions) == 0:
            actions.append(SQUARE * SQUARE)  # パス
        return actions

    def is_legal_action_xy(self, x, y, flip=False, success_flg=True):
        """任意のマスが合法手かどうか"""
        def is_legal_action_xy_dxy(x, y, dx, dy):
            """任意のマスの任意の方向が合法手かどうか"""
            # １つ目 相手の石
            x, y = x+dx, y+dy
            if y < 0 or (SQUARE - 1) < y or x < 0 or (SQUARE - 1) < x or \
                    self.enemy_pieces[x+y*SQUARE] != 1:
                return False

            # 2つ目以降
            for j in range(SQUARE):
                # 空
                if y < 0 or (SQUARE - 1) < y or x < 0 or (SQUARE - 1) < x or \
                        (self.enemy_pieces[x+y*SQUARE] == 0 and self.pieces[x+y*SQUARE] == 0):
                    return False

                # 自分の石
                if self.pieces[x+y*SQUARE] == 1:
                    # 反転
                    if flip:
                        for i in range(SQUARE):
                            x, y = x-dx, y-dy
                            if self.pieces[x+y*SQUARE] == 1:
                                return True
                            self.pieces[x+y*SQUARE] = 1
                            self.enemy_pieces[x+y*SQUARE] = 0
                    return True
                # 相手の石
                x, y = x+dx, y+dy
            return False

        def is_legal_action_xy_dxy_penalty(x, y, dx, dy):
            """任意のマスの任意の方向が合法手かどうか"""
            # １つ目 自分の石
            x, y = x+dx, y+dy
            if y < 0 or (SQUARE - 1) < y or x < 0 or (SQUARE - 1) < x or \
                    self.pieces[x+y*SQUARE] != 1:
                return False

            # 2つ目以降
            for j in range(SQUARE):
                # 空
                if y < 0 or (SQUARE - 1) < y or x < 0 or (SQUARE - 1) < x or \
                        (self.enemy_pieces[x+y*SQUARE] == 0 and self.pieces[x+y*SQUARE] == 0):
                    return False

                # 相手の石
                if self.enemy_pieces[x+y*SQUARE] == 1:
                    # 反転
                    if flip:
                        for i in range(SQUARE):
                            x, y = x-dx, y-dy
                            if self.enemy_pieces[x+y*SQUARE] == 1:
                                return True
                            self.enemy_pieces[x+y*SQUARE] = 1
                            self.pieces[x+y*SQUARE] = 0
                    return True
                # 自分の石
                x, y = x+dx, y+dy
            return False

        # 空きなし
        if self.enemy_pieces[x+y*SQUARE] == 1 or self.pieces[x+y*SQUARE] == 1:
            return False

        # 石を置く
        if flip:
            # 確率で石が置けるかどうか
            if success_flg:
                # 確率 p
                self.pieces[x+y*SQUARE] = 1
            else:
                # 確率 1 - p
                self.enemy_pieces[x+y*SQUARE] = 1

                for dx, dy in self.dxy:
                    is_legal_action_xy_dxy_penalty(x, y, dx, dy)
                return False

        # 任意の位置が合法手かどうか
        flag = False
        for dx, dy in self.dxy:
            if is_legal_action_xy_dxy(x, y, dx, dy):
                flag = True
        return flag

    def is_first_player(self):
        """先手かどうか"""
        return self.depth % 2 == 0

    def __str__(self):
        """文字列表示"""
        ox = (u'\u25CF', u'\u25CB') if self.is_first_player() else (
            u'\u25CB', u'\u25CF')
        str = ''
        for i in range(SQUARE * SQUARE):
            if self.pieces[i] == 1:
                str += ox[0]
            elif self.enemy_pieces[i] == 1:
                str += ox[1]
            else:
                str += '-'
            if i % SQUARE == (SQUARE - 1):
                str += '\n'
        return str


def random_action(state: State):
    """ランダムで行動選択"""
    legal_actions = state.legal_actions()
    return legal_actions[np.random.randint(0, len(legal_actions))]


# 動作確認
@ watch.watch
def main():
    # 状態の生成
    state = State()

    # ゲーム終了までのループ
    while True:
        # ゲーム終了時
        if state.is_done():
            break

        # 次の状態の取得
        state = state.next(random_action(state), np.random.rand())
        # 文字列表示
        print(state)
        print()


if __name__ == '__main__':
    np.random.seed(seed=32)
    for i in range(2):
        main()
