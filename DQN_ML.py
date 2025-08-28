import numpy as np
import pandas as pd
import gym
from gym import spaces
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt

import pandas as pd 
from tvDatafeed import TvDatafeed,Interval


tv = TvDatafeed()
nifty_data=tv.get_hist('NIFTY','NSE',interval=Interval.in_1_minute,n_bars=5000)
df = nifty_data.copy()
df = df.drop(columns=['symbol'])
df.reset_index(drop=True, inplace=True)
df = df.rename(columns={'open':'Open','high': 'High','low': 'Low','close': 'Close','volume': 'Volume'})


# Normalize OHLCV columns
features = ['Open', 'High', 'Low', 'Close', 'Volume']
df[features] = df[features].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

# ---- Environment Definition ----
class StockTradingEnv(gym.Env):
    def __init__(self, df):
        super(StockTradingEnv, self).__init__()
        self.df = df
        self.current_step = 0
        self.action_space = spaces.Discrete(3)  # Buy, Sell, Hold
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)
        
    def reset(self):
        self.current_step = 0
        return self._get_observation()
    
    def _get_observation(self):
        return self.df.iloc[self.current_step].values.astype(np.float32)
    
    def step(self, action):
        reward = 0
        done = False
        current_price = self.df.iloc[self.current_step]['Close']
        
        if self.current_step < len(self.df) - 1:
            next_price = self.df.iloc[self.current_step + 1]['Close']
            if action == 0:  # Buy
                reward = next_price - current_price
            elif action == 1:  # Sell
                reward = current_price - next_price
            # Hold gets 0 reward
        else:
            done = True

        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            done = True
        
        return self._get_observation(), reward, done, {}

# ---- DQN Agent ----
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = []
        self.memory_limit = 2000
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(32, input_dim=self.state_size, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
        return model

    def remember(self, state, action, reward, next_state, done):
        if len(self.memory) >= self.memory_limit:
            self.memory.pop(0)
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.choice(self.action_size)
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        indices = np.random.choice(len(self.memory), self.batch_size, replace=False)
        for i in indices:
            state, action, reward, next_state, done = self.memory[i]
            state = np.reshape(state, [1, self.state_size])
            next_state = np.reshape(next_state, [1, self.state_size])

            target = reward
            if not done:
                target += self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])

            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# ---- Main Training Loop ----
env = StockTradingEnv(df)
state_size = env.observation_space.shape[0]
action_size = env.action_space.n
agent = DQNAgent(state_size, action_size)

episodes = 100
reward_history = []

for e in range(episodes):
    state = env.reset()
    state = np.reshape(state, [1, state_size])
    total_reward = 0

    while True:
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, [1, state_size])
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward

        if done:
            print(f"Episode {e+1}/{episodes} - Total Reward: {total_reward:.2f}")
            reward_history.append(total_reward)
            break

    agent.replay()

# ---- Plotting Reward Trend ----
plt.plot(reward_history)
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Reward Over Episodes')
plt.grid(True)
plt.show()
