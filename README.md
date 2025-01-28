# Multi-Agent Reinforcement Learning Project

This project builds upon:  
1. [OpenAI Baselines](https://github.com/openai/baselines)  
2. [pybullet-gym](https://github.com/benelot/pybullet-gym)

---

## My Contributions and Added Functionality

### Key Features:
1. **Multi-Agent System**:
   - The project supports simultaneous training of **N agents**, each with its own neural network.
   - Run separate instances of the program with different `agent_number` parameters from multiple terminals.
2. **Custom Environment**:
   - The custom environment file is located in `pybulletgym/envs/roboschool/robots/locomotors/`.

---

### Latest Version Highlights:
1. **Agent Interaction**:
   - **Red agent** runs away from the **green agent**, the **green agent** runs away from the **blue agent**, and the **blue agent** runs away from the **red agent**.
   - **Results**: Check `results/2019-11-22 16-19-10.flv` after ~1 hour of training. While not perfect, agents demonstrate learned behavior.
2. **Training Command**:
   To replicate the experiment:
   ```bash
   python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
   python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
   python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=3
   ```
3. **Multi-Agent Implementation**:
   - Uses `ppo2/muag_n.py` for **N agents** (replacing the older two-agent implementation `ppo2/muag.py`).

---

## TODO

1. **Hindsight Experience Replay (HER)**:
   - Implement HER, which involves a dictionary-based observation structure with keys like `obs` and `desired`.

2. **Simulated Agent Vision**:
   - Enable agents to perceive their surroundings based on their simulated position and orientation.

3. **Different Timescales**:
   - Introduce hierarchical control:
     - **Blue agent** gives instructions (e.g., target points) to the **red agent** every 100 steps.
     - **Red agent** is rewarded for reaching the target.
     - **Blue agent** is rewarded for the **red agent's** presence at the target during specific intervals.

---

## Installation

To set up the project, follow these steps:

```bash
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
virtualenv ~/new5 --python=python3.5
. ~/new5/bin/activate

cd ~/new5
python3.5 -m pip install tensorflow-gpu==1.14
git clone https://github.com/openai/baselines.git
cd ~/new5/baselines
python3.5 -m pip install -e .

python3.5 -m pip install gym==0.14
python3.5 -m pip install gym[atari]

cd ~/new5
git clone https://github.com/benelot/pybullet-gym.git
cd pybullet-gym
python3.5 -m pip install -e .
# For initial modifications, see the file "Как что работает.txt"

python3.5 -m baselines.run --alg=ppo2 --env=HumanoidPyBulletEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/HumanoidPyBulletEnv-v0_2e7_ppo2 --play
```

---

## Notes

For additional setup details and implementation specifics, refer to `Как что работает.txt`. If you encounter issues, please feel free to reach out for assistance or discussion.

---

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for more details.
