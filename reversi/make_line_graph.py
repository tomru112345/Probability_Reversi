import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

plt.style.use('default')
sns.set()
sns.set_style('whitegrid')
sns.set_palette('Set1')

y = []
for i in range(11):
    y.append(i)

x = np.array(y)

# 勝率 = 勝利数 / （勝利数 + 敗戦数） (後攻の勝率)
# turn = True
turns = [True, False]

for turn in turns:
    # 最適方策同士(後攻)の結果
    if turn:
        optimal_win = [10000, 8799, 7970, 7008,
                       6346, 5749, 5325, 5056, 4518, 4479, 4706]
        optimal_lose = [0, 1036, 1929, 2827, 3399,
                        3906, 4325, 4571, 5092, 5130, 4958]
    else:
        optimal_lose = [10000, 8799, 7970, 7008,
                        6346, 5749, 5325, 5056, 4518, 4479, 4706]
        optimal_win = [0, 1036, 1929, 2827, 3399,
                       3906, 4325, 4571, 5092, 5130, 4958]
    if turn:
        # ランダム方策(後攻)の勝率
        random_win = [1527, 995, 1973, 2199, 2469,
                      2542, 2899, 3038, 3043, 3375, 3664]
        random_lose = [8365, 8679, 7673, 7436, 7097,
                       6985, 6684, 6480, 6456, 6135, 5861]
    else:
        # ランダム方策(先攻)の勝率
        random_win = [0, 857, 1544, 2263, 2686,
                      3086, 3372, 3817, 3783, 3931, 4002]
        random_lose = [10000, 9096, 8341, 7580,
                       7049, 6592, 6246, 5808, 5832, 5657, 5563]

    if turn:
        # 学習データ(200)(後攻)の勝率
        ai_200_win = [8176, 6283, 5272, 4762, 3900,
                      4696, 4092, 3715, 3585, 3594, 3561]
        ai_200_lose = [1824, 3047, 3881, 4426, 5429,
                       4888, 5306, 5732, 5999, 5939, 5951]
    else:
        # 学習データ(200)(先攻)の勝率
        ai_200_win = [0, 905, 1735, 2363, 3061,
                      3590, 3954, 4074, 4145, 4064, 4248]
        ai_200_lose = [10000, 8943, 8116, 7414, 6689,
                       6063, 5673, 5522, 5486, 5511, 5343]

    if turn:
        # 学習データ(400)(後攻)の勝率
        ai_400_win = [8386, 6848, 5707, 5293, 4442,
                      4501, 3828, 3989, 3572, 3886, 3952]
        ai_400_lose = [1614, 2645, 3541, 4207, 4883,
                       5030, 5399, 5419, 5943, 5645, 5629]
    else:
        # 学習データ(400)(先攻)の勝率
        ai_400_win = [0, 846, 1740, 2309, 3162,
                      3632, 3846, 4099, 4237, 3871, 4201]
        ai_400_lose = [10000, 8982, 8077, 7508, 6582,
                       6080, 5832, 5539, 5362, 5729, 5397]

    if turn:
        # 学習データ(600)(後攻)の勝率
        ai_600_win = [9050, 1634, 5573, 4986, 4786,
                      4223, 4274, 4048, 3724, 3768, 3967]
        ai_600_lose = [950, 7990, 3360, 4369, 4714,
                       5122, 5177, 5506, 5841, 5788, 5587]
    else:
        # 学習データ(600)(先攻)の勝率
        ai_600_win = [0, 969, 1689, 2442, 3254,
                      3469, 4022, 4142, 4343, 4250, 4210]
        ai_600_lose = [10000, 8898, 8123, 7351, 6500,
                       6187, 5609, 5442, 5240, 5364, 5390]

    optimal_win_late = [0] * 11
    random_win_late = [0] * 11
    ai_200_win_late = [0] * 11
    ai_400_win_late = [0] * 11
    ai_600_win_late = [0] * 11

    for i in range(11):
        optimal_win_late[i] = optimal_win[i] / \
            (optimal_win[i] + optimal_lose[i])
        random_win_late[i] = random_win[i] / (random_win[i] + random_lose[i])
        ai_200_win_late[i] = ai_200_win[i] / (ai_200_win[i] + ai_200_lose[i])
        ai_400_win_late[i] = ai_400_win[i] / (ai_400_win[i] + ai_400_lose[i])
        ai_600_win_late[i] = ai_600_win[i] / (ai_600_win[i] + ai_600_lose[i])

    gene_1 = np.array(optimal_win_late)
    gene_2 = np.array(random_win_late)
    gene_3 = np.array(ai_200_win_late)
    gene_4 = np.array(ai_400_win_late)
    gene_5 = np.array(ai_600_win_late)

    df = pd.DataFrame({
        'x': x,
        'gene_1': gene_1,
        'gene_2': gene_2,
        'gene_3': gene_3,
        'gene_4': gene_4,
        'gene_5': gene_5
    })

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot('x', 'gene_1', data=df, label='最適方策同士', marker='o')
    ax.plot('x', 'gene_2', data=df, label='ランダム方策', marker='o')
    ax.plot('x', 'gene_3', data=df, label='200周学習データ', marker='o')
    ax.plot('x', 'gene_4', data=df, label='400周学習データ', marker='o')
    ax.plot('x', 'gene_5', data=df, label='600周学習データ', marker='o')
    # ax.legend(prop={"family": "MS Gothic"})
    ax.set_xlabel("確率の設定値", fontname="MS Gothic")
    if turn:
        ax.set_ylabel("後攻の勝率", fontname="MS Gothic")
    else:
        ax.set_ylabel("先攻の勝率", fontname="MS Gothic")
    ax.set_ylim(0.0, 1.0)
    # plt.show()
    save_path = f'./line_graph/'
    os.makedirs(save_path, exist_ok=True)  # フォルダがない時は生成
    if turn:
        plt.savefig(save_path + '{}.png'.format("AI_SecondRowWinRate"))
    else:
        plt.savefig(save_path + '{}.png'.format("AI_FirstRowWinRate"))

    ax.legend(prop={"family": "MS Gothic"})
    if turn:
        plt.savefig(save_path + '{}.pdf'.format("AI_SecondRowWinRate"))
    else:
        plt.savefig(save_path + '{}.pdf'.format("AI_FirstRowWinRate"))
    plt.close()
