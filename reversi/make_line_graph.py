import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

plt.style.use('default')
sns.set()
sns.set_style('whitegrid')
sns.set_palette('Set1')

y = []
for i in range(11):
    y.append(i)

x = np.array(y)

# 勝率 = 勝利数 / （勝利数 + 敗戦数） (後攻の勝率)

# 最適方策同士の結果
optimal_win = [10000, 8799, 7970, 7008, 6346, 5749, 5325, 5056, 4518, 4479, 4706]
optimal_lose = [0, 1036, 1929, 2827, 3399, 3906, 4325, 4571, 5092, 5130, 4958]

# ランダム方策(後攻)の勝率
random_win = [1527, 995, 1973, 2199, 2469, 2542, 2899, 3038, 3043, 3375, 3664]
random_lose = [8365, 8679, 7673, 7436, 7097, 6985, 6684, 6480, 6456, 6135, 5861]

# ランダム方策(先攻)の勝率
# random_win = [0, 857, 1544, 2263, 2686, 3086, 3372, 3817, 3783, 3931, 4002]
# random_lose = [10000, 9096, 8341, 7580, 7049, 6592, 6246, 5808, 5832, 5657, 5563]

# 学習データ(200)(後攻)の勝率
ai_win = [1864, 5272, 4762, 3900, 4696, 4092]
ai_lose = [7615, 3881, 4426, 5429, 4888, 5306]

# 学習データ(200)(先攻)の勝率
ai_win = [928, 1735, 2363, 3061, 3590, 3954]
ai_lose = [8927, 8116, 7414, 6689, 6063, 5673]

optimal_win_late = [0] * 11
random_win_late = [0] * 11
for i in range(11):
    optimal_win_late[i] = optimal_win[i] / (optimal_win[i] + optimal_lose[i])
    random_win_late[i]  = random_win[i] / (random_win[i] + random_lose[i])
gene_1 = np.array(optimal_win_late)
gene_2 = np.array(random_win_late)
# gene_2 = np.array([2.1, 2.4, 2.3, 2.1, 2.2, 2.1])
# gene_3 = np.array([0.3, 0.6, 1.1, 1.8, 2.2, 2.8])

df = pd.DataFrame({
    'x': x,
    'gene_1': gene_1,
    'gene_2': gene_2,
    # 'gene3': gene_3
})

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.plot('x', 'gene_1', data=df, label='最適方策同士', marker='o')
ax.plot('x', 'gene_2', data=df, label='ランダム方策', marker='o')
# ax.plot('x', 'gene3', data=df, label='gene 3', marker='o')
ax.legend(prop={"family":"MS Gothic"})
ax.set_xlabel("確率の設定値", fontname="MS Gothic")
ax.set_ylabel("後攻の勝率", fontname="MS Gothic")
ax.set_ylim(0, 1)
plt.show()