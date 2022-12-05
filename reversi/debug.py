from game import State
# from cppState import State
from collections import defaultdict
from settings import default_ratio_box
from typing import List
from datetime import datetime
from pathlib import Path
import sys
import pickle
import gc
import itertools


# def load_data():
#     """学習データの読み込み"""
#     history_path = sorted(
#         Path(f'./policy_iteration_data/').glob('*.history'))[-1]
#     with history_path.open(mode='rb') as f:
#         return pickle.load(f)

# history = load_data()
# pi: dict = history[0]
# V: dict = history[1]
# del history
# gc.collect()

n_0 = [-1, 0, 1]
n_1 = [-1, 1]
all_board = itertools.product(n_0, n_0, n_0, n_0, n_0, n_1,
                              n_1, n_0, n_0, n_1, n_1, n_0, n_0, n_0, n_0, n_0)

cnt = 0
for board in all_board:
    print('\reval_onestep {}/{}'.format(cnt + 1, 8503056), end='')
    cnt += 1