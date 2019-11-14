import numpy as np
from baselines.common.runners import AbstractEnvRunner
import time
import pickle
import os

def save_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)

def safe_getsize(fname):
    success = 0
    while not success:
        try:
            ans = os.path.getsize(fname)
            success = 1
        except FileNotFoundError:
            pass
    return ans

def safe_write_to_file(fname, txt):
    success = 0
    while not success:
        try:
            with open(fname, 'w') as file:
                file.write(txt) 
            success = 1
        except FileNotFoundError:
            pass

def safe_save_obj(obj, name, agent_number, active_process_fname='active_process.txt'):
    success = 0
    while not success:
        active_process = safe_getsize(active_process_fname)
        if active_process == agent_number:
            save_obj(obj, name)
            success = 1
    active_process = 3 - agent_number
    safe_write_to_file(active_process_fname, '.' * active_process)

def safe_load_obj(name, agent_number, active_process_fname='active_process.txt'):
    success = 0
    while not success:
        active_process = safe_getsize(active_process_fname)
        if active_process == agent_number:
            obj = load_obj(name)
            success = 1
    active_process = 3 - agent_number
    safe_write_to_file(active_process_fname, '.' * active_process)
    return obj

class Runner(AbstractEnvRunner):
    """
    We use this object to make a mini batch of experiences
    __init__:
    - Initialize the runner

    run():
    - Make a mini batch
    """
    def __init__(self, *, env, model, nsteps, gamma, lam, agent_number):
        super().__init__(env=env, model=model, nsteps=nsteps)
        # Lambda used in GAE (General Advantage Estimation)
        self.lam = lam
        # Discount rate
        self.gamma = gamma
        self.agent_number = agent_number

    def run(self):
        # Here, we init the lists that will contain the mb of experiences
        mb_obs, mb_rewards, mb_actions, mb_values, mb_dones, mb_neglogpacs = [],[],[],[],[],[]
        mb_states = self.states
        epinfos = []
        # For n in range number of steps
        self.time2 = time.time()
        self.time_muag = 0
        self.time_else = 0
        for cur_step in range(self.nsteps):
            # Given observations, get action value and neglopacs
            # We already have self.obs because Runner superclass run self.obs[:] = env.reset() on init
            actions, values, self.states, neglogpacs = self.model.step(self.obs, S=self.states, M=self.dones)
            print('actions = ', actions)
            print('cur_step = ', cur_step, ',  agent_number = ', self.agent_number)
            
            self.time1 = time.time()
            self.time_else += self.time1 - self.time2
            print('It took ', self.time_else, ' seconds for everything else')
            if self.agent_number != 0:
                actions = actions[0] ## they are packed as [[...]]
                actions_agentTHIS_fname = '/home/ai/new5/baselines/baselines/actions_agent' + str(self.agent_number) + '.pkl'
                actions_agentTHAT_fname = '/home/ai/new5/baselines/baselines/actions_agent' + str(3 - self.agent_number) + '.pkl'
                if cur_step == 0:
                    if self.agent_number == 1:
                        for finame in ['active_process.txt', 'actions_agent1.pkl', 'actions_agent2.pkl']:
                            if os.path.isfile(finame):
                                os.remove(finame)
                    actions_agentTHIS = {}
                    if not os.path.isfile('active_process.txt'):
                        with open('active_process.txt', 'w') as file:
                            file.write('.' * self.agent_number)  ##agN=1 => '',    agN=2  => '...................<...>.................'
                else:
                    actions_agentTHIS = safe_load_obj(actions_agentTHIS_fname, agent_number = self.agent_number)  
                actions_agentTHIS[cur_step] = actions
                safe_save_obj({cur_step: actions}, actions_agentTHIS_fname, agent_number = self.agent_number)
                synch_success = 0
                while not synch_success:
                    if os.path.isfile(actions_agentTHAT_fname) and os.path.getsize(actions_agentTHAT_fname):
                        actions_agentTHAT = safe_load_obj(actions_agentTHAT_fname, agent_number = self.agent_number)
                        if cur_step in actions_agentTHAT.keys():
                            synch_success = 1
                    else:
                        #time.sleep(0.5)
                        pass
                actions_len = len(actions_agentTHIS[cur_step])
                if self.agent_number == 1:
                    actions = np.concatenate((actions_agentTHIS[cur_step][:actions_len//2]  ,  actions_agentTHAT[cur_step][actions_len//2:]))
                if self.agent_number == 2:
                    actions = np.concatenate((actions_agentTHAT[cur_step][:actions_len//2]  ,  actions_agentTHIS[cur_step][actions_len//2:]))
                actions = [actions] ## they were packed as [[...]]
            self.time2 = time.time()
            self.time_muag += self.time2 - self.time1
            print('It took ', self.time_muag, ' seconds to modify actions for multiagency')
            
            mb_obs.append(self.obs.copy())
            mb_actions.append(actions)
            mb_values.append(values)
            mb_neglogpacs.append(neglogpacs)
            mb_dones.append(self.dones)

            # Take actions in env and look the results
            # Infos contains a ton of useful informations
            self.obs[:], rewards, self.dones, infos = self.env.step(actions)
            self.env.render()
            for info in infos:
                maybeepinfo = info.get('episode')
                if maybeepinfo: epinfos.append(maybeepinfo)
            mb_rewards.append(rewards)
        #batch of steps to batch of rollouts
        mb_obs = np.asarray(mb_obs, dtype=self.obs.dtype)
        mb_rewards = np.asarray(mb_rewards, dtype=np.float32)
        mb_actions = np.asarray(mb_actions)
        mb_values = np.asarray(mb_values, dtype=np.float32)
        mb_neglogpacs = np.asarray(mb_neglogpacs, dtype=np.float32)
        mb_dones = np.asarray(mb_dones, dtype=np.bool)
        last_values = self.model.value(self.obs, S=self.states, M=self.dones)

        # discount/bootstrap off value fn
        mb_returns = np.zeros_like(mb_rewards)
        mb_advs = np.zeros_like(mb_rewards)
        lastgaelam = 0
        for t in reversed(range(self.nsteps)):
            if t == self.nsteps - 1:
                nextnonterminal = 1.0 - self.dones
                nextvalues = last_values
            else:
                nextnonterminal = 1.0 - mb_dones[t+1]
                nextvalues = mb_values[t+1]
            delta = mb_rewards[t] + self.gamma * nextvalues * nextnonterminal - mb_values[t]
            mb_advs[t] = lastgaelam = delta + self.gamma * self.lam * nextnonterminal * lastgaelam
        mb_returns = mb_advs + mb_values
        return (*map(sf01, (mb_obs, mb_returns, mb_dones, mb_actions, mb_values, mb_neglogpacs)),
            mb_states, epinfos)
# obs, returns, masks, actions, values, neglogpacs, states = runner.run()
def sf01(arr):
    """
    swap and then flatten axes 0 and 1
    """
    s = arr.shape
    return arr.swapaxes(0, 1).reshape(s[0] * s[1], *s[2:])


