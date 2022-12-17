from game import State
# from cppState import State
from settings import default_ratio_box
from datetime import datetime
from pathlib import Path
import sys
import pickle
import os
import itertools
import gc

def load_data():
    """学習データの読み込み"""
    history_path = sorted(
        Path(f'./human_play/').glob('*.history'))[-1]
    with history_path.open(mode='rb') as f:
        return pickle.load(f)


l = load_data()
print(l[0])
print(l[1])