from game import State
# from cppState import State
from collections import defaultdict
from settings import default_ratio_box
from typing import List
from datetime import datetime
from pathlib import Path
import sys
import pickle
import os
import itertools


# def load_data():
#     """学習データの読み込み"""
#     history_path = sorted(
#         Path(f'./policy_iteration_data/').glob('*.history'))[-1]
#     with history_path.open(mode='rb') as f:
#         return pickle.load(f)


# data = load_data()
# print(data)
b = [i for i in range(100000000)]
