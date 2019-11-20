Проект создается на основе:<br/>
(1) https://github.com/openai/baselines<br/>
(2) https://github.com/benelot/pybullet-gym

## **Установка проекта велась так:**
```
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
#см. начальные изменения после установки в файле "Как что работает.txt"

python3.5 -m baselines.run --alg=ppo2 --env=HumanoidPyBulletEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/HumanoidPyBulletEnv-v0_2e7_ppo2 --play
## РАБОТАЕТ
```

## **Общее описание этой и последних версий:**
(1) Возможность запустить одновременно 2 агентов, за каждый отвечает отдельная нейросеть.
Просто запускаются из двух отдельных терминалов две версии программы, отличающиеся только параметром agent_number:
```
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
```
(2) CustomEnv лежит в pybulletgym/envs/roboschool/robots/locomotors/<br/>

**Особенности последней версии по сравнению с прошлой:**
Красный агент убегает от синего. Вполне обучается. Движения агентов ограничены кругом. Скорость красного агента выше в 2 раза.<br/>
Конкретно эта версия запускалась командой:<br/>
```
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
```
Результаты лежат в файле results/2019-11-20 16-07-10.flv<br/>

**TODO:**
(1) Хочется попробовать то же на HER (hindsight experience replay).<br/>
В HER особенная структура возвращаемого obs:  это dictionary с ключами 'obs', 'desired' (goal) итп.
(2) Обобщить мультиагентность на нескольких агентов