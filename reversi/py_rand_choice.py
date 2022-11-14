import numpy as np

def choice(a, p):
    action: int = np.random.choice(a=a, p=p)
    return action