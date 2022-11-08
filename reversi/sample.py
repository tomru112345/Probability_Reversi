from mcts import MCTS

xs = [1.0, 0.0, 0.5]

mcts = MCTS(1.0)
xs = mcts.boltzman(xs)
print(xs)
