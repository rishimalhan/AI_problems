import gym
from gym import spaces
import pandas as pd
import numpy as np

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

class StockTradingEnv(gym.Env):
	metadata = {'render.modes': ['human']}

	def __init__(self,stock_data):
		self.stock_data = stock_data
		self.action_space = spaces.Box( low=np.array([0,0]), high=np.array([3,1]), dtype=np.float16 )
		self.observation_space = spaces.Box( low=0, high=1, shape=(6,6), dtype=np.float16 )
		return

	def reset(self):
		return



if __name__=='__main__':
	metadata = {'render.modes': ['human']}

	# stock_data = pd.read_csv('aapl.csv')
	# stock_data = stock_data.sort_values('Date')
	
	# # The algorithms require a vectorized environment to run
	# env = DummyVecEnv([lambda: StockTradingEnv(stock_data)])

	# model = PPO2(MlpPolicy, env, verbose=1)
	# model.learn(total_timesteps=20000)
	# obs = env.reset()
	# for i in range(2000):
	#   action, _states = model.predict(obs)
	#   obs, rewards, done, info = env.step(action)
	#   env.render()