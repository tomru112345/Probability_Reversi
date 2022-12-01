from game import State
from collections import defaultdict
from settings import default_ratio_box
import numpy as np
import random
import itertools


class Reversi_State:
    def __init__(self, pieces=None, enemy_pieces=None, ratio_box=None, board=None, flg=True):
        """初期化"""
        # 方向定数
        self.dxy = ((1, 0), (1, 1), (0, 1), (-1, 1),
                    (-1, 0), (-1, -1), (0, -1), (1, -1))
        self.pieces = pieces
        self.enemy_pieces = enemy_pieces
        self.ratio_box = ratio_box
        self.pass_end = False
        self.board = board
        self.flg = flg

    def set_board(self, board):
        self.board = board
        pieces_tmp = [0] * 16
        enemy_pieces_tmp = [0] * 16
        for i in range(len(board)):
            if board[i] == 1:
                pieces_tmp[i] = 1
            elif board[i] == -1:
                enemy_pieces_tmp[i] = 1
        self.pieces = pieces_tmp
        self.enemy_pieces = enemy_pieces_tmp

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
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 16 or self.pass_end

    def check_pass(self):
        state = Reversi_State(self.pieces.copy(),
                              self.enemy_pieces.copy(), self.ratio_box.copy(), self.board.copy())
        action_l = state.legal_actions()
        if action_l == [16]:
            w = state.pieces
            state.pieces = state.enemy_pieces
            state.enemy_pieces = w
            if state.legal_actions() == [16]:
                self.pass_end = True
        return self.pass_end

    def next(self, action):
        """次の状態の取得"""
        state = Reversi_State(self.pieces.copy(),
                              self.enemy_pieces.copy(), self.ratio_box.copy())

        if action != 16:  # パスを選択していないとき
            state.is_legal_action_xy(action % 4, int(action/4), True)
        w = state.pieces
        state.pieces = state.enemy_pieces
        state.enemy_pieces = w

        # 2回連続パス判定
        if action == 16 and state.legal_actions() == [16]:
            state.pass_end = True

        return state

    def legal_actions(self):
        """合法手のリストの取得"""
        actions = []
        for j in range(0, 4):
            for i in range(0, 4):
                if self.is_legal_action_xy(i, j):
                    actions.append(i+j*4)
        if len(actions) == 0:
            actions.append(16)  # パス
        return actions

    def is_legal_action_xy(self, x, y, flip=False):
        """任意のマスが合法手かどうか"""
        def is_legal_action_xy_dxy(x, y, dx, dy):
            """任意のマスの任意の方向が合法手かどうか"""
            # １つ目 相手の石
            x, y = x+dx, y+dy
            if y < 0 or 3 < y or x < 0 or 3 < x or \
                    self.enemy_pieces[x+y*4] != 1:
                return False

            # 2つ目以降
            for j in range(4):
                # 空
                if y < 0 or 3 < y or x < 0 or 3 < x or \
                        (self.enemy_pieces[x+y*4] == 0 and self.pieces[x+y*4] == 0):
                    return False

                # 自分の石
                if self.pieces[x+y*4] == 1:
                    # 反転
                    if flip:
                        for i in range(4):
                            x, y = x-dx, y-dy
                            if self.pieces[x+y*4] == 1:
                                return True
                            self.pieces[x+y*4] = 1
                            self.enemy_pieces[x+y*4] = 0
                    return True
                # 相手の石
                x, y = x+dx, y+dy
            return False

        def is_legal_action_xy_dxy_penalty(x, y, dx, dy):
            """任意のマスの任意の方向が合法手かどうか"""
            # １つ目 自分の石
            x, y = x+dx, y+dy
            if y < 0 or 3 < y or x < 0 or 3 < x or \
                    self.pieces[x+y*4] != 1:
                return False

            # 2つ目以降
            for j in range(4):
                # 空
                if y < 0 or 3 < y or x < 0 or 3 < x or \
                        (self.enemy_pieces[x+y*4] == 0 and self.pieces[x+y*4] == 0):
                    return False

                # 相手の石
                if self.enemy_pieces[x+y*4] == 1:
                    # 反転
                    if flip:
                        for i in range(4):
                            x, y = x-dx, y-dy
                            if self.enemy_pieces[x+y*4] == 1:
                                return True
                            self.enemy_pieces[x+y*4] = 1
                            self.pieces[x+y*4] = 0
                    return True
                # 自分の石
                x, y = x+dx, y+dy
            return False

        # 空きなし
        if self.enemy_pieces[x+y*4] == 1 or self.pieces[x+y*4] == 1:
            return False

        # 石を置く
        if flip:
            # 確率で石が置けるかどうか
            if (random.random() * 100) <= self.ratio_box[x+y*4]:
                # 確率 p を引いたことを保持する
                self.ratio_flg = True

                self.pieces[x+y*4] = 1
            else:
                # 確率 1 - p を引いたことを保持する
                self.ratio_flg = False

                self.enemy_pieces[x+y*4] = 1
                for dx, dy in self.dxy:
                    is_legal_action_xy_dxy_penalty(x, y, dx, dy)
                return False

        # 任意の位置が合法手かどうか
        flag = False
        for dx, dy in self.dxy:
            if is_legal_action_xy_dxy(x, y, dx, dy):
                flag = True
        return flag

    def __str__(self):
        """文字列表示"""
        str = ''
        for i in range(16):
            if self.board[i] == 1:
                str += 'o'
            elif self.board[i] == -1:
                str += 'x'
            else:
                str += '-'
            if i % 4 == 3:
                str += '\n'
        return str


n_0 = [-1, 0, 1]
n_1 = [-1, 1]
all_board = list(itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                                   n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0))

# board = [-1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, 0, -1, -1, 0, -1]
# pieces = [0] * 16
# enemy_pieces = [0] * 16
# for i in range(len(board)):
#     if board[i] == 1:
#         pieces[i] = 1
#     elif board[i] == -1:
#         enemy_pieces[i] = 1
# state = Reversi_State(pieces, enemy_pieces, default_ratio_box, board)
# print(state.check_pass())
# print(state)


def first_player_value(state: Reversi_State, next_state: Reversi_State):
    """先手プレイヤーの価値"""
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if not state.is_lose():
        if next_state.is_lose():
            return -1.0 if next_state.flg else 1.0
    return 0.0


class Agent:
    def __init__(self, flg: bool):
        """初期化"""
        self.gamma = 0.9
        self.pi = defaultdict(lambda: {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                              7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0})
        self.V = defaultdict(lambda: 0)
        self.flg_first_player = flg

    def set_pi(self, state: State):
        if self.pi[state] == {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                              7: 0.0, 8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}:
            tmp_d = {}
            legal_action_list = state.legal_actions()
            action_num = len(legal_action_list)
            for i in range(0, 17):
                if i in legal_action_list:
                    tmp_d[i] = 1.0 / float(action_num)
                else:
                    tmp_d[i] = 0.0
            self.pi[state] = tmp_d


def eval_onestep(pi: defaultdict, V: defaultdict, gamma: float, flg: bool = True):
    for board in all_board:
        board = list(board)
        pieces = [0] * 16
        enemy_pieces = [0] * 16
        for i in range(len(board)):
            if board[i] == 1:
                pieces[i] = 1
            elif board[i] == -1:
                enemy_pieces[i] = 1
        state = Reversi_State(pieces, enemy_pieces,
                              default_ratio_box, board, flg)

        if state.check_pass():
            V[state] = 0  # 終了したときの価値関数は常に 0
            continue

        action_probs = pi[state]
        new_V = 0

        for action, action_prob in action_probs.items():
            next_state: Reversi_State = state.next(action)
            if flg:
                reward = first_player_value(state, next_state)
            else:
                reward = - (first_player_value(state, next_state))
            new_V += action_prob * (reward + gamma * V[next_state])

        V[state] = new_V
    return V


def policy_eval(pi: defaultdict, V: defaultdict, state: Reversi_State, gamma: float, threshold: float = 0.001, flg: bool = True):
    while True:
        old_V = V.copy()  # 更新前の価値関数
        V = eval_onestep(pi, V, gamma, flg)
        # 更新された量の最大値を求める
        delta = 0
        for state in V.keys():
            t = abs(V[state] - old_V[state])
            if delta < t:
                delta = t

        # 値と比較
        if delta < threshold:
            break
    return V


def argmax(d: dict):
    """argmax 関数"""
    max_value = max(d.values())
    max_key = 0
    for key, value in d.items():
        if value == max_value:
            max_key = key
    return max_key


def greedy_policy(V: defaultdict, gamma: float, flg: bool = True):
    pi = {}
    for board in all_board:
        board = list(board)
        pieces = [0] * 16
        enemy_pieces = [0] * 16
        for i in range(len(board)):
            if board[i] == 1:
                pieces[i] = 1
            elif board[i] == -1:
                enemy_pieces[i] = 1
        state = Reversi_State(pieces, enemy_pieces,
                              default_ratio_box, board, flg)

        action_values = {}
        action_list = state.legal_actions()
        for action in action_list:
            next_state = state.next(action)
            if state.is_first_player() == flg:
                reward = first_player_value(state, next_state)
            else:
                reward = - (first_player_value(state, next_state))
            value = reward + gamma * V[next_state]
            action_values[action] = value
        max_action = argmax(action_values)
        action_probs = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0,
                        8: 0.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0}
        action_probs[max_action] = 1.0
        pi[state] = action_probs
    return pi


def policy_iter(pi: defaultdict, V: defaultdict, state: Reversi_State, gamma: float, threshold: float = 0.001, flg: bool = True):
    while True:
        V = policy_eval(pi, V, state=state, gamma=gamma,
                        threshold=threshold, flg=flg)
        new_pi = greedy_policy(V, state=state, gamma=gamma, flg=flg)

        if new_pi == pi:
            break
        pi = new_pi
    return pi, V


def main(num):
    agent_1 = Agent(flg=False)
    for i in range(num):
        state = State()
        while True:
            # ゲーム終了時
            if state.is_done():
                break

            agent_1.set_pi(state)
            print(agent_1.pi[state])
            pi, V = policy_iter(agent_1.pi, agent_1.V, state,
                                gamma=0.9, flg=agent_1.flg_first_player)
            agent_1.pi = pi
            agent_1.V = V

            d = agent_1.pi[state]
            l_i = []
            l_d = []
            for a, b in d.items():
                l_i.append(a)
                l_d.append(b)
            state = state.next(np.random.choice(l_i, p=l_d))
            # print(state)

    # 動作確認
# if __name__ == '__main__':
    # モデルの読み込み
    # 状態の生成
    # main(1)
    # state = State()
    # rs = Reversi_State(state=state)
    # print(rs.state)
