#!/usr/bin/env python3
# Complete FRP-PPO Implementation for AMD GPUs
import torch
import numpy as np
import gymnasium as gym
from torch import nn, optim
from collections import deque
import math
import time
import argparse
from torch.distributions import Normal
from typing import Tuple

# AMD GPU Configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch.backends.cuda.matmul.allow_tf32 = True

class FRPCyclicBuffer:
    def __init__(self, p: int, env_obs_shape: Tuple[int], action_shape: Tuple[int]):
        self.p = p
        self.buffer_size = p - 1
        self.ptr = 0
        
        # FRP Schedule Generation
        self.schedule = self._generate_frp_schedule(p)
        
        # AMD Optimized Storage
        self.states = torch.zeros((self.buffer_size, *env_obs_shape), 
                                device=device, dtype=torch.float32)
        self.actions = torch.zeros((self.buffer_size, *action_shape),
                                 device=device, dtype=torch.float32)
        self.rewards = torch.zeros(self.buffer_size, device=device, dtype=torch.float32)
        self.next_states = torch.zeros((self.buffer_size, *env_obs_shape),
                                      device=device, dtype=torch.float32)
        self.dones = torch.zeros(self.buffer_size, device=device, dtype=torch.bool)
        self.log_probs = torch.zeros(self.buffer_size, device=device, dtype=torch.float32)
        self.values = torch.zeros(self.buffer_size, device=device, dtype=torch.float32)

    def _generate_frp_schedule(self, p: int) -> torch.Tensor:
        """Generate full-period cyclic sequence using FRP properties"""
        sequence = []
        remainder = 1
        for _ in range(p-1):
            sequence.append((remainder * 10) // p)
            remainder = (remainder * 10) % p
        return torch.tensor(sequence, device=device, dtype=torch.long) % (p-1)

    def add(self, state: np.ndarray, action: np.ndarray, reward: float, 
           next_state: np.ndarray, done: bool, log_prob: float, value: float):
        idx = self.schedule[self.ptr]
        self.states[idx] = torch.as_tensor(state, device=device)
        self.actions[idx] = torch.as_tensor(action, device=device)
        self.rewards[idx] = torch.tensor(reward, device=device)
        self.next_states[idx] = torch.as_tensor(next_state, device=device)
        self.dones[idx] = torch.tensor(done, device=device)
        self.log_probs[idx] = torch.tensor(log_prob, device=device)
        self.values[idx] = torch.tensor(value, device=device)
        self.ptr = (self.ptr + 1) % self.buffer_size

    def sample_batch(self, batch_size: int) -> Tuple[torch.Tensor]:
        indices = self.schedule[:batch_size]
        return (
            self.states[indices],
            self.actions[indices],
            self.rewards[indices],
            self.next_states[indices],
            self.dones[indices],
            self.log_probs[indices],
            self.values[indices]
        )

class PPOPolicy(nn.Module):
    def __init__(self, obs_dim: int, action_dim: int):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
            nn.Tanh()
        )
        self.critic = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
        self.log_std = nn.Parameter(torch.zeros(action_dim, device=device))

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.actor(x), self.critic(x)

    def act(self, state: np.ndarray) -> Tuple[np.ndarray, float, torch.Tensor]:
        state_t = torch.as_tensor(state, dtype=torch.float32, device=device)
        with torch.no_grad():
            action_mean = self.actor(state_t)
            value = self.critic(state_t)
        
        action_std = torch.exp(self.log_std)
        dist = Normal(action_mean, action_std)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(-1)
        
        return action.cpu().numpy(), log_prob.item(), value.squeeze()

class FRP_PPO_Trainer:
    def __init__(self, env_name: str = "Pendulum-v1", p: int = 4099, 
                gamma: float = 0.99, gae_lambda: float = 0.95):
        self.env = gym.make(env_name)
        self.policy = PPOPolicy(self.env.observation_space.shape[0],
                               self.env.action_space.shape[0]).to(device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=3e-4)
        self.buffer = FRPCyclicBuffer(p, self.env.observation_space.shape,
                                     self.env.action_space.shape)
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.epochs = 10
        self.clip_eps = 0.2
        self.target_kl = 0.01
        
        # Compile critical paths for AMD GPU
        if torch.cuda.is_available():
            self.policy = torch.compile(self.policy, mode='max-autotune')

    def compute_advantages(self, rewards: torch.Tensor, values: torch.Tensor,
                         dones: torch.Tensor, next_values: torch.Tensor) -> torch.Tensor:
        deltas = torch.zeros_like(rewards, device=device)
        advantages = torch.zeros_like(rewards, device=device)
        last_gae = 0.0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[t].float()
                next_value = next_values[t]
            else:
                next_non_terminal = 1.0 - dones[t+1].float()
                next_value = values[t+1]
                
            delta = rewards[t] + self.gamma * next_value * next_non_terminal - values[t]
            deltas[t] = delta
            advantages[t] = last_gae = delta + self.gamma * self.gae_lambda * next_non_terminal * last_gae
        
        return (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    def update_policy(self, batch_size: int):
        states, actions, rewards, next_states, dones, old_log_probs, values = \
            self.buffer.sample_batch(batch_size)
        
        with torch.no_grad():
            next_values = self.policy.critic(next_states).squeeze()
        
        advantages = self.compute_advantages(rewards, values, dones, next_values)
        returns = advantages + values

        for _ in range(self.epochs):
            current_values = self.policy.critic(states).squeeze()
            action_means = self.policy.actor(states)
            action_std = torch.exp(self.policy.log_std)
            dist = Normal(action_means, action_std)
            new_log_probs = dist.log_prob(actions).sum(-1)
            entropy = dist.entropy().sum(-1).mean()

            ratios = (new_log_probs - old_log_probs).exp()
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.clip_eps, 1+self.clip_eps) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()

            critic_loss = 0.5 * (current_values - returns).pow(2).mean()

            kl = (old_log_probs - new_log_probs).mean()
            if kl > self.target_kl:
                break

            loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()

        return actor_loss.item(), critic_loss.item(), entropy.item()

    def collect_experience(self, num_steps: int):
        state, _ = self.env.reset()
        for _ in range(num_steps):
            action, log_prob, value = self.policy.act(state)
            next_state, reward, done, _, _ = self.env.step(action)
            
            self.buffer.add(state, action, reward, next_state, done, log_prob, value)
            
            state = next_state if not done else self.env.reset()[0]

    def benchmark(self, num_episodes: int = 20) -> float:
        total_reward = 0.0
        for _ in range(num_episodes):
            state, _ = self.env.reset()
            episode_reward = 0.0
            done = False
            
            while not done:
                with torch.no_grad():
                    action, _, _ = self.policy.act(state)
                state, reward, done, _, _ = self.env.step(action)
                episode_reward += reward
            
            total_reward += episode_reward
        
        return total_reward / num_episodes

    def train(self, total_steps: int = 1_000_000, batch_size: int = 4096,
             log_interval: int = 10):
        start_time = time.time()
        step_count = 0
        
        while step_count < total_steps:
            # Collection Phase
            self.collect_experience(batch_size)
            step_count += batch_size

            # Training Phase
            actor_loss, critic_loss, entropy = self.update_policy(batch_size)

            # Benchmarking
            if (step_count // batch_size) % log_interval == 0:
                avg_reward = self.benchmark()
                time_elapsed = time.time() - start_time
                steps_per_sec = step_count / time_elapsed
                
                print(f"Step {step_count}/{total_steps} | "
                      f"Avg Reward: {avg_reward:.2f} | "
                      f"Actor Loss: {actor_loss:.3f} | "
                      f"Critic Loss: {critic_loss:.3f} | "
                      f"Entropy: {entropy:.3f} | "
                      f"Steps/s: {steps_per_sec:.0f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FRP-PPO Training on AMD GPUs')
    parser.add_argument('--env', type=str, default='Pendulum-v1',
                      help='Gym environment name')
    parser.add_argument('--p', type=int, default=10007,
                      help='Full reptend prime for buffer size')
    parser.add_argument('--batch-size', type=int, default=4096,
                      help='Training batch size')
    parser.add_argument('--total-steps', type=int, default=1_000_000,
                      help='Total training steps')
    args = parser.parse_args()

    trainer = FRP_PPO_Trainer(env_name=args.env, p=args.p)
    trainer.train(total_steps=args.total_steps, batch_size=args.batch_size)