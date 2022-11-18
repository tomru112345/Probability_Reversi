import numpy as np

def choice(legal_actions, scores):
    action: int = np.random.choice(a=legal_actions, p=scores)
    return action