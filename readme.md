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
(1) Возможность запустить одновременно 2 агентов, за каждый отвечает отдельная нейросеть.
Просто запускаются из двух отдельных терминалов две версии программы, отличающиеся только параметром agent_number:
```
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
```
(2) CustomEnv лежит в pybulletgym/envs/roboschool/robots/locomotors/<br/>
Задача агентов - стремиться каждый к своей точке.

**Особенности последней версии по сравнению с прошлой:**
Конкретно эта версия запускалась командой:<br/>
```
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=1
python3.5 -m baselines.run --alg=ppo2 --env=CustomEnv-v0 --network=mlp --num_timesteps=2e7 --save_path=~/models/AntPyBulletEnv-v0_ppo2 --play --agent_number=2
```
ИСПРАВЛЕНИЕ ОШИБКИ ДЛЯ МУЛЬТИАГЕНТНОСТИ (2019-11-20--13-50)<br/>
Раньше в ppo2/runner.py просто менялось action = muag_change_actions(...)<br/>
    но это приводило к ошибке -- в мультиагентном сценарии агент номер 1 не мог даже учиться стоять в в заданной точке<br/>
    (в то время как тот же запуск с agent_number==0 обучался этому в пределах 2-3 минут)<br/>
Исправлено на action_for_sim = muag_change_actions(...)<br/>
    причем actions_for_sim используется только для подачи на вход симулятора env.step()<br/>
Предположительный источник ошибки и почему она исправлена:<br/>
    поскольку в прошлом варианте нейросеть обучалась на действиях обоих агентов,<br/>
    то это могло приводить к возникновению нежеланных корреляций и смещенностей<br/>
    (хотя действия 2го агента и не вытекали явно из вычислений нейросетки 1го агента, но неявно корреляции могли быть)<br/>
    А в новом варианте вторая часть действий 1го агента просто абсолютно никак ни на что не влияет и не скоррелирована ни с чем<br/>
    следовательно и корреляций и нежеланных смещенностей быть не должно<br/>
Что и иллюстрируется в коммите на примере задачки стремления агентов каждого к своей точке.<br/>
В дальнейшем это описание будет в файле "Как что работает.txt"<br/>

**TODO:**
(1) Хочется попробовать то же на HER (hindsight experience replay).<br/>
В HER особенная структура возвращаемого obs:  это dictionary с ключами 'obs', 'desired' (goal) итп.