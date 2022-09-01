from stable_baselines3 import DQN
from env import OthelloEnv


env = OthelloEnv()
model = DQN.load(f"./result/rl_model_30000_steps")

done = False
obs = env.reset()
# print(model.predict(obs))
while not done:
    action, state = model.predict(obs)
    obs, reward, done, info_police = env.step(action=action)
    env.render()
    if done:
        print(reward)
        break
env.close()
