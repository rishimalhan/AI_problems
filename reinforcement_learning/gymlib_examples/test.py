# import gym

# env = gym.make('CartPole-v0')
# obs = env.reset()
# print(env.observation_space.low)
# print(env.observation_space.high)

# # obs, reward, done, info = env.step( env.action_space.sample() )
# # print(reward)
# # print(done)

# env.close()
# # print( env.action_space )


from gym import spaces

space = spaces.Discrete(8)  # Set with 8 elements {0, 1, 2, ..., 7}
x = space.sample()
print(x)
assert space.contains(x)
assert space.n == 8
