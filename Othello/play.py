from env import OthelloEnv


env = OthelloEnv()
done = False
while not done:
        env.render()
        obs, rewards, done, info_police = env.step(action=int(input()))
        # env.render()
        if done:
            break
# env.close()
