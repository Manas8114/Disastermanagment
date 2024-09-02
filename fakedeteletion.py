import gym
from gym import spaces
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import os

class FakeDetectionEnv(gym.Env):
    def __init__(self, csv_path):
        super(FakeDetectionEnv, self).__init__()

        # Load data from CSV
        self.data = pd.read_csv(csv_path)
        
        # Handle missing values by filling them with an empty string
        self.data['Summary'] = self.data['Summary'].fillna('')

        # Extract summaries
        self.summaries = self.data['Summary'].values

        # Use TF-IDF to convert summaries to vectors
        self.vectorizer = TfidfVectorizer(max_features=300)
        self.vectorized_summaries = self.vectorizer.fit_transform(self.summaries).toarray()

        # Define action space: 0 for 'real', 1 for 'fake'
        self.action_space = spaces.Discrete(2)
        
        # Define observation space based on vector size
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.vectorized_summaries.shape[1],), dtype=np.float32)

        # Initialize environment state
        self.current_index = 0
        self._seed = None

    def step(self, action):
        # Get current summary vector
        current_summary_vector = self.vectorized_summaries[self.current_index]
        
        # Placeholder for reward calculation
        reward = 1 if action == np.random.randint(2) else -1

        # Move to the next summary
        self.current_index += 1
        done = self.current_index >= len(self.vectorized_summaries)

        return current_summary_vector, reward, done, {}

    def reset(self):
        # Reset index and return the first summary vector
        self.current_index = 0
        return self.vectorized_summaries[self.current_index]

    def render(self, mode='human'):
        pass

    def seed(self, seed=None):
        # Set the seed for reproducibility
        self._seed = seed
        np.random.seed(self._seed)

# Provide the correct file path to your CSV
csv_path = r'C:\\java\\disaster managment\\disaster_news.csv'

# Create environment with the CSV file path
env = FakeDetectionEnv(csv_path)

# Wrap the environment for vectorized processing
env = make_vec_env(lambda: env, n_envs=1)

# Define the RL model
model = PPO('MlpPolicy', env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Save the model
model_path = "fake_detection_model_with_csv"
model.save(model_path)

# Print confirmation message
print(f"Model successfully saved to {model_path}")

# Optional: Remove any fake data or temporary files if needed
# For example, if there were temporary files or logs you wanted to clean up
# os.remove('path_to_temporary_file')  # Uncomment if you have such files to remove
