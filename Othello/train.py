from env import Env

env = Env()

while not env.done:
    env.render()
    done = env.step(action=int(input()))
    if done:
        break
