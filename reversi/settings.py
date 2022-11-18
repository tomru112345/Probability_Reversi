import random
# 4 以上の 2 の倍数
SQUARE = 4

default_ratio_box = [10] * SQUARE * SQUARE


def create_ratiobox_set_value(p: int = 10):
    "決まった盤面での学習用"
    ratio_num = 3
    for x in range(SQUARE * SQUARE):
        default_ratio_box[x] = 100 - ratio_num * p
        if ratio_num == 7:
            ratio_num = 3
        else:
            ratio_num += 1


create_ratiobox_set_value(3)


def create_ratiobox(p: int = 10):
    for x in range(SQUARE * SQUARE):
        default_ratio_box[x] = 100 - (random.randrange(0, 9) * p)


# 普通のオセロの条件
# default_ratio_box = [100] * SQUARE * SQUARE

# ai 同士の対戦用ファイルパス
file1 = f'./model/best.h5'
file2 = f'./model/best.h5'
