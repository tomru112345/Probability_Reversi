class LerningMachine(Agent):
    WINNER_SCORE = 1000.0   # 勝利時の褒章スコア
    DEFAULT_ALPHA = 0.1  # 学習レート（スコア変動）は 1 割
    DEFAULT_GAMMA = 0.9  # 続行時のスコア変動レート
    DEFAULT_EPSILON = 0.3 # ランダムで置き場所を決定する確率

    def __init__(self, board, color):
        super().__init__(board, color)
        self._turn = 0
        self._last_board = None
        self._last_attack = None
        self._q = Quantity(LerningMachine.DEFAULT_ALPHA, LerningMachine.DEFAULT_GAMMA)
        self._e = LerningMachine.DEFAULT_EPSILON

    def lerning(self, selectables, latest_board):
        if self._last_board is None:
            return  # 初手は学習対象外
        if self._board.is_game_end():
            # ゲーム終了してるなら、勝利か敗北かでスコア加算
            if self._board.is_win(self._color):
                # 勝利してれば前回の手（状態と着手手）にスコア加算
                self._q.add_fee(self._last_board, self._last_attack, LerningMachine.WINNER_SCORE)
        else:
            # ゲーム継続中
            if len(selectables) == 0:
                # 選択不能って学習できなくね？
                # むしろこの状況は悪手
                max_q = 0
            else:
                # 選択できる手があるならそのまま学習
                qs = []
                for index in selectables:
                    # 一手先の評価値情報を取得
                    qs.append(self._q.select_q(latest_board, index))
                # 評価値の最大値を取得
                max_q = max(qs)
            # 前回の手（状態と着手手）を学習
            self._q.lerning(self._last_board, self._last_attack, max_q)

    def converted_board(self):
        cur = self._color
        enemy = ReversiBoard.STONE_BLACK
        if cur == enemy:
            enemy = ReversiBoard.STONE_WHITE
        board_str = self._board.to_string()
        return board_str.replace(cur, 'S').replace(enemy, 'E')

    def put(self):
        self._turn += 1
        # 既存状態の確認
        current_board = self.converted_board()
        ables = self._board.able_to_puts(self._color)

        # 学習と次の手の準備
        self.lerning(ables, current_board)
        self._last_board = current_board

        # 次が打てないと諦め
        length = len(ables)
        if length == 0:
            return

        # 次の一手
        if random.random() < self._e:
            # 一定確率でランダム行動選択
            if length == 1:
                x, y = ables[0]
                self._last_attack = ables[0]
                self._board.put_stone(self._color, x, y)
            else:
                x, y = ables[random.randint(0, len(ables) - 1)]
                self._last_attack = (x, y)
                self._board.put_stone(self._color, x, y)
        else:
            # さもなくば、評価値の最もいいものを選択
            # 評価値リスト作成
            qs = []
            for index in ables:
                qs.append(self._q.select_q(current_board, index))
            
            # 最高座標を探す
            max_q = max(qs)
            if qs.count(max_q) > 1:
                # 同値 MAX の座標がある場合
                # max_q の座標からランダム決定
                vals = [i for i in range(len(ables)) if qs[i] == max_q]
                i = random.choice(vals)
            else:
                # MAX は一つしかない
                i = qs.index(max_q)
            # 移動先座標確定
            self._last_attack = ables[i]
            x, y = self._last_attack
            self._board.put_stone(self._color, x, y)