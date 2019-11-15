import pickle
import os
import numpy as np

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

def muag_change_actions(actions, cur_step, agent_number, curr_directory):
    actions = actions[0] ## they are packed as [[...]]
    actions_agentTHIS_fname = os.path.join(curr_directory, 'actions_agent') + str(agent_number) + '.pkl'
    actions_agentTHAT_fname = os.path.join(curr_directory, 'actions_agent') + str(3 - agent_number) + '.pkl'
    if cur_step == 0:
        if agent_number == 1:
            for finame in ['active_process.txt', 'actions_agent1.pkl', 'actions_agent2.pkl']:
                if os.path.isfile(finame):
                    os.remove(finame)
        actions_agentTHIS = {}
        if not os.path.isfile('active_process.txt'):
            with open('active_process.txt', 'w') as file:
                file.write('.' * agent_number)  ##agN=1 => '',    agN=2  => '...................<...>.................'
    else:
        actions_agentTHIS = safe_load_obj(actions_agentTHIS_fname, agent_number = agent_number)  
    actions_agentTHIS[cur_step] = actions
    safe_save_obj({cur_step: actions}, actions_agentTHIS_fname, agent_number = agent_number)
    synch_success = 0
    while not synch_success:
        if os.path.isfile(actions_agentTHAT_fname) and os.path.getsize(actions_agentTHAT_fname):
            actions_agentTHAT = safe_load_obj(actions_agentTHAT_fname, agent_number = agent_number)
            if cur_step in actions_agentTHAT.keys():
                synch_success = 1
        else:
            #time.sleep(0.5)
            pass
    actions_len = len(actions_agentTHIS[cur_step])
    if agent_number == 1:
        actions = np.concatenate((actions_agentTHIS[cur_step][:actions_len//2]  ,  actions_agentTHAT[cur_step][actions_len//2:]))
    if agent_number == 2:
        actions = np.concatenate((actions_agentTHAT[cur_step][:actions_len//2]  ,  actions_agentTHIS[cur_step][actions_len//2:]))
    actions = [actions] ## they were packed as [[...]]
    return actions
