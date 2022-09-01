from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback
import time
from env import OthelloEnv


env = OthelloEnv()
model = DQN("MlpPolicy", env, verbose=1, tensorboard_log="log", device="auto")
print("start learning")
time_start = time.perf_counter()
checkpoint_callback = CheckpointCallback(
    save_freq=10000, save_path="./result/")
model.learn(total_timesteps=30000, callback=checkpoint_callback)
time_end = time.perf_counter()
print("finish learning")
print(time_end - time_start)
del model
