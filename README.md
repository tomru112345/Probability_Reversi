# Probability_Reversi

不確定完全情報ゲームである確率リバーシの深層強化学習に挑戦

## 必要パッケージのインストール

```bash
python -m pip install -r requirements.txt
```

## 深層学習

### 特徴

- 層の数が多くなる
  - 学習時間がかかる
- ユニット数が多くなる
  - 重要性の低い特徴を抽出して「過学習」になりやすい

## 学習率の確認方法

```bash
tensorboard --logdir=./Ohtello/log/
```

## Functional API

Sequential では分岐や複数の出力があるネットワーク構造は作成できない

- Functional API と呼ばれる複雑なモデルを定義するためのインターフェースを使用

```python
# モデルの作成
model = Sequential()
model.add(Dense(256, activation='sigmoid', input_shape=(784,)))
model.add(Dense(128, activation='sigmoid'))
model.add(Dropout(rate=0.5))
model.add(Dense(10, activation='softmax'))
```

```python
# モデルの作成
input = Input(shape=(784,))
x = Dense(256, activation='sigmoid')(input)
x = Dense(128, activation='sigmoid')(x)
x = Dropout(rate=0.5)(x)
x = Dense(10, activation='softmax')(x)
model = Model(inputs=input, outputs=x)
```

## 正則化

### L2 正則化

極端な「重み」を 0 に近づける

## 残差ブロックの生成



## 学習内容

### UCB1 アルゴリズム

UCB1 値: 成功率 + バイアス

```math
UCB1 = (\frac{w}{n}) + (2 \times \log \frac{t}{n})^{\frac{1}{2}}
```

## 参考文献

- [【強化学習】softmax行動選択](https://www.tcom242242.net/entry/ai-2/%E5%BC%B7%E5%8C%96%E5%AD%A6%E7%BF%92/softmax/)
- [スッキリわかるAlphaZero](https://horomary.hatenablog.com/entry/2021/06/21/000500)
- [MuZeroの実装解説（for Breakout）](https://horomary.hatenablog.com/entry/2021/08/04/205601)
