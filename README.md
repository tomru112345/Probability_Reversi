# Probability_Reversi

不確定完全情報ゲームである確率リバーシの深層強化学習に挑戦

## 参考論文

- [AlphaZero-inspired game learning: Faster training by using MCTS only at test time](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9893320&casa_token=rf3PGP-FzYwAAAAA:r4SJO2OdFAQVhRcmg0OCg8g0tLvvak3rimdrQGD5M3aXKVbODOEVCpVIsxCM6tDgcSP7rHGofmA)


## C++ の pybind11 用コマンド

```bash
g++ -O3 -Wall -shared -std=c++2a -fPIC `python3.10 -m pybind11 --includes` mctsbind.cpp -o cppMCTS`python3.10-config --extension-suffix` -I /usr/include/python3.10
```

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
tensorboard --logdir=./reversi/log/
```

## 学習速度の向上へ

実行速度を上げるために cython で書く

- [AlphaZeroで6x6オセロ](https://qiita.com/AokiMasataka/items/40868c7a09b8d67c3101)

## 参考文献

- [【強化学習】softmax行動選択](https://www.tcom242242.net/entry/ai-2/%E5%BC%B7%E5%8C%96%E5%AD%A6%E7%BF%92/softmax/)
- [今年49歳になるおっさんでも作れたAlphaZero](https://tail-island.github.io/programming/2018/06/20/alpha-zero.html)
- [“深層学習”ではなく“深層強化学習”が決め手 将棋界最強のAlphaZeroと互角の強さ「dlshogi」の秘密](https://logmi.jp/tech/articles/324191)
- [スッキリわかるAlphaZero](https://horomary.hatenablog.com/entry/2021/06/21/000500)
- [アルファ碁ゼロに使われているディープラーニングを解き明かす 論文から詳細を紹介](https://codezine.jp/article/detail/10952)
- [MuZeroの実装解説（for Breakout）](https://horomary.hatenablog.com/entry/2021/08/04/205601)
