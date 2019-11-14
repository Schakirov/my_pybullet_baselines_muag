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

## **Описание данной версии:**
В первую очередь - это модифицированный файл runner.py, позволяющий запустить одновременно 2 агентов, за каждый отвечает отдельная нейросеть.
Просто запускаются из двух отдельных терминалов две версии программы, отличающиеся только параметром agent_number:
```
python3.5 -m baselines.run --alg=ppo2 --env=AntPyBulletEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
python3.5 -m baselines.run --alg=ppo2 --env=AntPyBulletEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
```

**Особенности последней версии по сравнению с прошлой:**
Теперь у каждого agent_number собственная функция реворда.<br/>
Сделано это просто - любая функция имеет доступ к sys.argv, где определен agent_number.<br/>
В данной версии, агенты хотят быть как можно ближе к центру координат (в плане xy), и чтобы другой агент наоборот был как можно дальше от центра координат.<br/>

**TODO:**
(1) Хочется попробовать то же на HER (hindsight experience replay).<br/>
Для этого сначала хорошо бы вынести шеринг action в отдельную функцию, и мб в отдельный файл вообще, который импортировать.<br/>
Тогда для переноса в HER нужно будет только перенести этот импортируемый файл, и изменить несколько (~10 или чуть больше) строчек в HER<br/>
(2) И еще пожалуй надо заканчивать эпизод, как только агент слишком далеко от (0, 0)