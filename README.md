# Probability_Othello

## 学習率の確認方法

```bash
tensorboard --logdir=./Ohtello/log/
```

## 学習内容

### UCB1 アルゴリズム

UCB1 値: 成功率 + バイアス

```math
UCB1 = (\frac{w}{n}) + (2 \times \log \frac{t}{n})^{\frac{1}{2}}
```

## 参考文献

- [【強化学習】softmax行動選択](https://www.tcom242242.net/entry/ai-2/%E5%BC%B7%E5%8C%96%E5%AD%A6%E7%BF%92/softmax/)
