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

## active_process ALWAYS goes like 1, 2, ... , Nmax, 1, 2 ......  so it can either forever go through all n,  or forever stop at some n

def safe_save_obj(obj, name, agent_number, ag_max, active_process_fname='active_process.txt'):
    success = 0
    while not success:
        active_process = safe_getsize(active_process_fname)
        if active_process == agent_number:
            save_obj(obj, name)
            success = 1
    active_process = active_process + 1
    if active_process > ag_max:
        active_process = 1
    safe_write_to_file(active_process_fname, '.' * active_process)

def safe_loadADDsave_obj(name, agent_number, cur_step, actions, ag_max, active_process_fname='active_process.txt'):
    ## we want not to lose information about  cur_step in other agents  which we can lose if use  safe_save_obj
    success = 0
    while not success:
        active_process = safe_getsize(active_process_fname)
        if active_process == agent_number:
            if cur_step == 0 and agent_number == 1:
                new_obj = {1: {0: actions}}
            else:
                obj = load_obj(name)
                if agent_number not in obj.keys():
                    obj[agent_number] = {}
                obj[agent_number][cur_step] = actions  ##add new info not losing already existent
                new_obj = {}  ## we want to store only cur_step,  don't want 'agents_actions.pkl' to grow indefinetely
                for i in obj.keys():
                    new_obj[i] = {}
                    if cur_step in obj[i].keys():
                        new_obj[i][cur_step] = obj[i][cur_step]
            save_obj(new_obj, name)
            success = 1
    active_process = active_process + 1
    print('active_process = ', active_process)
    if active_process > ag_max:
        active_process = 1
    safe_write_to_file(active_process_fname, '.' * active_process)

def safe_load_obj(name, agent_number, ag_max, active_process_fname='active_process.txt'):
    success = 0
    while not success:
        active_process = safe_getsize(active_process_fname)
        if active_process == agent_number:
            obj = load_obj(name)
            success = 1
    active_process = active_process + 1
    if active_process > ag_max:
        active_process = 1
    safe_write_to_file(active_process_fname, '.' * active_process)
    return obj
'''
def muag_change_actions_stupid(actions, cur_step, agent_number, curr_directory, total_num_of_agents=2):
    ag_max = total_num_of_agents ## from 1 to ag_max inclusively
    actions = actions[0] ## they are packed as [[...]]
    actions_agent_fnames = [''] * (ag_max + 1)
    for i in range(1, ag_max):
        actions_agent_fnames[i]  = os.path.join(curr_directory, 'actions_agent') + str(i) + '.pkl'
    if cur_step == 0:
        if agent_number == 1:
            for finame in ['active_process.txt'] + actions_agent_fnames:
                if os.path.isfile(finame):
                    os.remove(finame)
            if not os.path.isfile('active_process.txt'):
                with open('active_process.txt', 'w') as file:
                    file.write('.' * 1) 
        actions_agentTHIS = {}
    else:
        actions_agentTHIS = safe_load_obj(actions_agent_fnames[agent_number], agent_number, ag_max)  
    actions_agentTHIS[cur_step] = actions
    safe_save_obj({cur_step: actions}, actions_agent_fnames[agent_number], agent_number, ag_max)
    for i in range(1, ag_max):
        ############################### stopped here temporarily
        synch_success = 0
        while not synch_success:
            if os.path.isfile(actions_agentTHAT_fname) and os.path.getsize(actions_agentTHAT_fname):
                actions_agentTHAT = safe_load_obj(actions_agentTHAT_fname, agent_number, ag_max)
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
    return actions'''

def muag_change_actions(actions, cur_step, agent_number, curr_directory, max_agents):
    print('0000')
    actions = actions[0] ## they are packed as [[...]]
    actions_agents_fname = os.path.join(curr_directory, 'actions_agents.pkl')
    print('000--11')
    if cur_step == 0 and agent_number == 1:
            for finame in ['active_process.txt', 'actions_agents.pkl']:
                if os.path.isfile(finame):
                    os.remove(finame)
            if not os.path.isfile('active_process.txt'):
                with open('active_process.txt', 'w') as file:
                    file.write('.' * 1)  ##agN=1 => '',    agN=2  => '...................<...>.................'
            actions_agents = {}
    else:
        actions_agents = safe_load_obj(actions_agents_fname, agent_number, max_agents)
    print('000-12')
    if cur_step == 0:
        if agent_number not in actions_agents.keys():
            actions_agents[agent_number] = {}
    print('000-13')
    actions_agents[agent_number][cur_step] = actions
    print('actions_agents = ', actions_agents)
    print('11111')
    safe_loadADDsave_obj(actions_agents_fname, agent_number, cur_step, actions, max_agents, 'active_process.txt')
    print('22222')
    synch_success = 0
    while not synch_success:
        if os.path.isfile(actions_agents_fname):
            actions_agents = safe_load_obj(actions_agents_fname, agent_number, max_agents)
            synch_success = 1
            for i in range(1, max_agents + 1):
                if i not in actions_agents.keys() or cur_step not in actions_agents[i].keys():
                    synch_success = 0
        else:
            #time.sleep(0.5)
            pass
    actions_len = len(actions_agents[agent_number][cur_step])
    actions = actions_agents[1][cur_step][:actions_len//max_agents]
    for i in range(2, max_agents + 1):
        actions = np.concatenate((actions, actions_agents[i][cur_step][   (i-1)*actions_len//max_agents : i*actions_len//max_agents   ]))
    actions = [actions] ## they were packed as [[...]]
    return actions

def muag_change_values(values, agent_number, max_agents):
    values_old = values
    values = 0 * values
    i = agent_number
    values[   (i-1)*len(values)//max_agents : i*len(values)//max_agents   ] = values_old[   (i-1)*len(values)//max_agents : i*len(values)//max_agents   ]
    return values