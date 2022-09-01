class Quantity:
    """Q 学習機本体"""
    def __init__(self, alpha, gamma, initial_q=50.0):
        """Q 値、学習係数、伝播係数の設定"""
        self._values = {}
        self._alpha = alpha
        self._gamma = gamma
        self._initial_q = initial_q

    def select_q(self, state, act):
        """状態とアクションをキーに、q 値取得"""
        if (state, act) in self._values:
            return self._values[(state, act)]
        else:
            # Q 値が未学習の状況なら、Q 初期値
            self._values[(state, act)] = self._initial_q
            return self._initial_q

    def save(self):
        with open('qlern.pickle', mode = 'wb') as f:
            pickle.dump(self._values, f)

    def load(self):
        with open('qlern.pickle', mode = 'rb') as f:
            self._values = pickle.load(f)

    def set(self, state, act, q_value):
        """Q 値設定"""
        self._values[(state, act)] = q_value

    def lerning(self, state, act, max_q):
        """Q 値更新"""
        pQ = self.select_q(state, act)
        new_q = pQ + self._alpha * (self._gamma * (max_q - pQ))
        self.set(state, act, new_q)

    def add_fee(self, state, act, fee):
        """報酬を与える"""
        pQ = self.select_q(state, act)
        new_q = pQ + self._alpha * (fee - pQ)
        self.set(state, act, new_q)