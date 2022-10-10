# 4 以上の 2 の倍数
SQUARE = 6

default_ratio_box = [10] * SQUARE * SQUARE
ratio_num = 10
for x in range(SQUARE * SQUARE):
    default_ratio_box[x] = ratio_num
    if ratio_num == 100:
        ratio_num = 10
    else:
        ratio_num += 10
