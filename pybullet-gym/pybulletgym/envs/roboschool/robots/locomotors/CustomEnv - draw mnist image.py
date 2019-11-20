import gym
from gym import spaces
import numpy as np
from tkinter import *
from PIL import Image, ImageTk, ImageFilter
import random
import time
import cv2

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
    self.action_space = spaces.Box( np.array([-1,-1,-1]), np.array([+1,+1,+1]) ) ## step_x, step_y,  erase/draw
    self.velocity = 0.01
    # Example for using image as input:
    #self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype=np.uint8)
    self.observation_space = spaces.Box( np.array([0,0,-1]), np.array([+1,+1,+1]) ) ## two coordinates - x, y  and prev_reward
    self.state = np.array([random.random(), random.random(), 0])
    self.prev_state = np.broadcast_to(self.state, (100,) + self.state.shape).copy()
    self.a = Tk()
    self.canv_w = 600
    self.canv_h = 600
    self.c = Canvas(self.a, bg='white', width=self.canv_w, height=self.canv_h)
    self.c.grid(row=1, columnspan=5)
    self.a.update()
    self.color_b = 0; self.color_g = 0; self.color_r = 0;
    self.attended = np.zeros((self.canv_w, self.canv_h))
    self.action = 0
    self.text_id = 0
    self.prev_potential = 0
    self.goal_image = cv2.imread('/home/ai/new5/pybullet-gym/pybulletgym/envs/roboschool/robots/locomotors/CustomEnvPicture.jpeg', cv2.IMREAD_GRAYSCALE)
    self.goal_image = cv2.resize(self.goal_image, (self.canv_w,self.canv_h)) / 255
    self.goal_image_orig = self.goal_image ## just to show
    self.goal_image = np.rot90(np.flipud(self.goal_image), 3)  ## arr[0, 0] shall be in left bottom of screen
    self.drawORerase = 1 ## 1 if draw, -1 if erase

  def step(self, action):
      self.action = action
      print('action = ', action)
      print('self.state = ', self.state)
      self.prev_state[:-1, :] = self.prev_state[1:, :]
      self.prev_state[-1, :] = self.state
      self.state[0] += self.velocity * action[0]
      self.state[1] += self.velocity * action[1]
      self.state[0] = self.state[0] % 1
      self.state[1] = self.state[1] % 1
      self.drawORerase = (action[2] < 0) * -1 + (0 <= action[2]) * +1
      self.potential = 0 - abs(0.7 - self.state[0]) - abs(0.3 - self.state[1])
      self.potential = - np.sum(abs(np.log(self.goal_image + 1/255) - np.log(self.attended/255 + 1/255)))
      #self.potential = - abs(np.pi/4 - self.state[2])
      reward = self.potential - self.prev_potential
      print('reward = ', reward)
      print('potential = ', self.potential)
      self.prev_potential = self.potential
      #reward = - abs(4 - action)
      self.state[2] = (reward < -1) * -1 + (-1 <= reward <=1) * reward + (1 < reward) * 1
      done = 0
      return self.state, reward, done, {}
  
  def reset(self):
      self.state = np.array([random.random(), random.random(), 0])
      return self.state

  def render(self, mode='human', close=False):
      '''self.color_r += random.randint(-20,20); self.color_r = self.color_r + (self.color_r < 0) * (0 - self.color_r) + (self.color_r > 255) * (255 - self.color_r)
      self.color_g += random.randint(-20,20); self.color_g = self.color_g + (self.color_g < 0) * (0 - self.color_g) + (self.color_g > 255) * (255 - self.color_g)
      self.color_b += random.randint(-20,20); self.color_b = self.color_b + (self.color_b < 0) * (0 - self.color_b) + (self.color_b > 255) * (255 - self.color_b)
      colorfill = get_rgb(self.color_r, self.color_g, self.color_b)'''
      if time.time() % 20 < 0.01:
        img =  ImageTk.PhotoImage(image=Image.fromarray(245 - np.rot90(np.flipud(self.attended), 3)))
        self.c.create_image(0,0,anchor="nw",image=img)
        self.a.update()
        time.sleep(2)
        img =  ImageTk.PhotoImage(image=Image.fromarray(245 - 255 * self.goal_image_orig)) ## 
        self.c.create_image(0,0,anchor="nw",image=img)
        self.a.update()
        time.sleep(2)
      for i in [-1 + len(self.prev_state)]:
          x_prev = self.prev_state[i-1][0];   y_prev = self.prev_state[i-1][1];
          x = self.prev_state[i][0];   y = self.prev_state[i][1];
          self.attended = self.fill_self_attended(x, y, x_prev, y_prev)
          if abs(x - x_prev) < 0.05 and abs(y - y_prev) < 0.05:
            colorfill_correspondence = 255 * self.goal_image[int(x * self.canv_w), int(y * self.canv_h)]
            colorfill = get_rgb(255 - colorfill_correspondence, colorfill_correspondence, 0)
            width_here = 3
            if self.drawORerase == -1:
                colorfill = get_rgb(colorfill_correspondence, 255 - colorfill_correspondence, 0)
                width_here = 2
            line_id = self.c.create_line(x_prev * self.canv_w, y_prev * self.canv_h, 
                                x * self.canv_w, y * self.canv_h, width=width_here, 
                                fill=colorfill, capstyle=ROUND, smooth=TRUE, splinesteps=36)
            self.c.after(1000, self.c.delete, line_id)
            if time.time() % 1 < 0.01:
                if self.text_id:
                    self.c.delete(self.text_id)
                self.text_id = self.c.create_text(100,10,fill="darkblue",font="Times 20 italic bold",
                            text=str(self.action))
      self.a.update()
  
  def fill_self_attended(self, x, y, x_prev, y_prev):
    self.attended[int(self.canv_w * x), int(self.canv_h * y)] = self.attended[int(self.canv_w * x), int(self.canv_h * y)] * 0.9999 + 25 * self.drawORerase
    if self.attended[int(self.canv_w * x), int(self.canv_h * y)]  < 0:
        self.attended[int(self.canv_w * x), int(self.canv_h * y)]  = 0  ##else reward function wouldn't be valid  (it uses log)
    return self.attended