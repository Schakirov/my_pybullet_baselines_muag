import gym
from gym import spaces
import numpy as np
from tkinter import *
from PIL import Image, ImageTk, ImageFilter
import random
import time
import cv2
import sys

def get_rgb(r,g,b):
    print(r,g,b)
    ans = '#'
    for i in [r,g,b]:
        if i > 15:
            add = hex(int(i))[2:]
        else:
            add = '0' + hex(int(i))[2:]
        ans += add
    return ans

def get_agent_number(args):
    ans = 0 #by default
    for elem in args:
        if elem[:-1] == '--agent_number=':
            ans = elem[-1]
    return int(ans)

def get_distance(x1, y1, x2, y2):
    a = np.linalg.norm([x2 - x1, y2 - y1])
    b = np.linalg.norm([1 - abs(x2 - x1), y2 - y1])
    c = np.linalg.norm([x2 - x1, 1 - abs(y2 - y1)])
    d = np.linalg.norm([1 - abs(x2 - x1), 1 - abs(y2 - y1)])
    return min(a,b,c,d)

def fit_to_01(arr, indices):
    for i in indices:
        arr[i] = (0 < arr[i] < 1) * arr[i] + (1 <= arr[i]) * 1
    return arr

def fit_to_circle(arr, indices, xyR):
    ## xyR is like [x, y, R]  of the circle
    arr = np.array(arr)
    for i in indices:
        r = np.linalg.norm(arr[i] - xyR[:2])
        if r > xyR[2]:
            arr[i] = xyR[:2] + (arr[i] - xyR[:2]) * xyR[2] / r
    return arr
                

class CustomEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}

  def __init__(self):
    super(CustomEnv, self).__init__()
    # Define action and observation space
    # They must be gym.spaces objects
    # Example when using discrete actions:
    #self.N_DISCRETE_ACTIONS = 5
    #self.action_space = spaces.Discrete(self.N_DISCRETE_ACTIONS)
    self.agent_num = get_agent_number(sys.argv)
    self.action_space = spaces.Box( np.array([-1,-1,-1,-1]), np.array([+1,+1,+1,+1]) ) ## step_x, step_y,  step_x, step_y
    self.velocity_red = 0.01  #escaping agent has higher velocity
    self.velocity_blue = 0.005
    # Example for using image as input:
    #self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)
    self.observation_space = spaces.Box( np.array([0,0,-1,0,0,-1]), np.array([+1,+1,+1,+1,+1,+1]) ) ## two coordinates - x, y  and prev_reward - for both agents
    self.state = np.array([0.25, 0.25, 0,   0.5, 0.5, 0])
    self.prev_state = np.broadcast_to(self.state, (100,) + self.state.shape).copy()
    self.a = Tk()
    self.canv_w = 600
    self.canv_h = 600
    self.c = Canvas(self.a, bg='white', width=self.canv_w, height=self.canv_h)
    self.c.grid(row=1, columnspan=5)
    self.a.update()
    self.color_b = 0; self.color_g = 0; self.color_r = 0;
    self.action = 0
    self.text_id = 0
    self.line_ids = [None] * 10  #length
    self.prev_potential = 0
    self.time_sleep = 0
    button1 = Button(self.a, text = "speed", command = self.onButton, anchor = W)
    button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
    button1_window = self.c.create_window(400, 10, anchor=NW, window=button1)

  def step(self, action):
      na = self.agent_num
      self.action = action
      print('action = ', action)
      print('self.state = ', self.state)
      self.prev_state[:-1, :] = self.prev_state[1:, :]
      self.prev_state[-1, :] = self.state
      self.state[0] += self.velocity_red * action[0];   self.state[3] += self.velocity_blue * action[2];   
      self.state[1] += self.velocity_red * action[1];   self.state[4] += self.velocity_blue * action[3];   
      #self.state[0] = self.state[0] % 1;   self.state[3] = self.state[3] % 1;   
      #self.state[1] = self.state[1] % 1;   self.state[4] = self.state[4] % 1;   
      self.state = fit_to_01(self.state, [0,1,3,4])
      self.state = fit_to_circle(self.state, [[0,1],[3,4]], [0.5, 0.5, 0.5])
      self.potential = abs(self.state[0] - self.state[3]) + abs(self.state[1] - self.state[4])
      #self.potential = - np.linalg.norm([self.state[0] - 0.25, self.state[1] - 0.25])
      #self.potential = - abs(self.state[0] - 0.25) - abs(self.state[1] - 0.25)
      #self.potential = get_distance(self.state[0], self.state[1], self.state[3], self.state[4])
      if self.agent_num == 2:
          self.potential = - self.potential  ## 2nd agent has an opposite goal
          #self.potential = - np.linalg.norm([0.2 - self.state[3], 0.2 - self.state[4]])
          #self.potential = - abs(self.state[3] - 0.2) - abs(self.state[4] - 0.2)
      reward = self.potential - self.prev_potential
      print('reward = ', reward)
      print('potential = ', self.potential)
      self.prev_potential = self.potential
      #reward = - abs(4 - action)
      self.state[2] = (reward < -1) * -1 + (-1 <= reward <=1) * reward + (1 < reward) * 1
      done = 0
      return self.state, reward, done, {}
  
  def reset(self):
      self.state = np.array([0.25, 0.25, 0,   0.5, 0.5, 0])
      return self.state

  def render(self, mode='human', close=False):
      time.sleep(self.time_sleep)
      '''self.color_r += random.randint(-20,20); self.color_r = self.color_r + (self.color_r < 0) * (0 - self.color_r) + (self.color_r > 255) * (255 - self.color_r)
      self.color_g += random.randint(-20,20); self.color_g = self.color_g + (self.color_g < 0) * (0 - self.color_g) + (self.color_g > 255) * (255 - self.color_g)
      self.color_b += random.randint(-20,20); self.color_b = self.color_b + (self.color_b < 0) * (0 - self.color_b) + (self.color_b > 255) * (255 - self.color_b)
      colorfill = get_rgb(self.color_r, self.color_g, self.color_b)'''
      for rendering_agent in [1, 2]:
        ra = rendering_agent
        for i in [-1 + len(self.prev_state)]:
            x_prev = self.prev_state[i-1][0+3*(ra-1)];   y_prev = self.prev_state[i-1][1+3*(ra-1)];
            x = self.prev_state[i][0+3*(ra-1)];   y = self.prev_state[i][1+3*(ra-1)];
            if abs(x - x_prev) < 0.05 and abs(y - y_prev) < 0.05:
                colorfill = 'red'
                if ra == 2:
                    colorfill = 'blue'
                line_id = self.c.create_line(x_prev * self.canv_w, y_prev * self.canv_h, 
                                    x * self.canv_w, y * self.canv_h, width=3, 
                                    fill=colorfill, capstyle=ROUND, smooth=TRUE, splinesteps=36)
                #self.c.after(10, self.c.delete, line_id)
                if self.line_ids[0] != None:
                    self.c.delete(self.line_ids[0])
                self.line_ids = self.line_ids[1:] + [line_id]
                if time.time() % 1 < 0.01:
                    if self.text_id:
                        self.c.delete(self.text_id)
                    self.text_id = self.c.create_text(100,10,fill="darkblue",font="Times 20 italic bold",
                                text=str(self.action))
      self.a.update()

  def onButton(self):
      self.time_sleep += 0.05
      if self.time_sleep > 0.3:
          self.time_sleep = 0
      pass