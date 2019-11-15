import gym
from gym import spaces

class CustomEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}

  def __init__(self):
    super(CustomEnv, self).__init__()
    # Define action and observation space
    # They must be gym.spaces objects
    # Example when using discrete actions:
    N_DISCRETE_ACTIONS = 2
    self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
    # Example for using image as input:
    #self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)
    self.observation_space = spaces.Discrete(10)  ## from 0 to 9
    self.state = 0

  def step(self, action):
      self.state += action * 2 - 1
      if self.state > 9:
          self.state = 9
      if self.state < 0:
          self.state = 0
      reward = self.state
      done = self.state == 0
      return self.state, reward, done, {}
  
  def reset(self):
      self.state = 0
      return self.state

  def render(self, mode='human', close=False):
      print(self.state)