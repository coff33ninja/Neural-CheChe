"""
Experience replay buffer for storing and sampling training data
"""

from collections import deque
import random
import numpy as np


class SharedReplayBuffer:
    """Shared replay buffer for storing game experiences"""
    
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def add(self, experiences):
        """Add a list of experiences to the buffer"""
        if isinstance(experiences, list):
            self.buffer.extend(experiences)
        else:
            self.buffer.append(experiences)
    
    def sample(self, batch_size):
        """Sample a batch of experiences"""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def get_statistics(self):
        """Get statistics about the replay buffer"""
        if not self.buffer:
            return {
                "mean_reward": 0,
                "std_reward": 0,
                "total_experiences": 0,
                "buffer_utilization": 0.0
            }
        
        rewards = np.array([exp[2] for exp in self.buffer if exp[2] is not None])
        
        stats = {
            "mean_reward": np.mean(rewards) if len(rewards) > 0 else 0,
            "std_reward": np.std(rewards) if len(rewards) > 0 else 0,
            "total_experiences": len(self.buffer),
            "buffer_utilization": len(self.buffer) / self.capacity,
            "reward_distribution": (
                np.histogram(rewards, bins=10)[0].tolist() if len(rewards) > 0 else []
            ),
        }
        
        return stats
    
    def clear(self):
        """Clear all experiences from the buffer"""
        self.buffer.clear()
    
    def __len__(self):
        """Get the number of experiences in the buffer"""
        return len(self.buffer)
    
    def is_full(self):
        """Check if the buffer is at capacity"""
        return len(self.buffer) >= self.capacity
    
    def get_recent_experiences(self, n=100):
        """Get the n most recent experiences"""
        if n >= len(self.buffer):
            return list(self.buffer)
        return list(self.buffer)[-n:]
    
    def get_experience_quality_metrics(self):
        """Analyze the quality of stored experiences"""
        if not self.buffer:
            return {}
        
        try:
            # Analyze policy diversity
            policy_entropies = []
            for exp in self.buffer:
                if len(exp) > 1 and isinstance(exp[1], dict):
                    policy = exp[1]
                    probs = list(policy.values())
                    if probs:
                        # Calculate entropy as a measure of policy diversity
                        probs = np.array(probs)
                        probs = probs / np.sum(probs)  # Normalize
                        entropy = -np.sum(probs * np.log(probs + 1e-10))
                        policy_entropies.append(entropy)
            
            metrics = {
                "avg_policy_entropy": np.mean(policy_entropies) if policy_entropies else 0,
                "policy_diversity": np.std(policy_entropies) if policy_entropies else 0,
                "num_analyzed": len(policy_entropies)
            }
            
            return metrics
            
        except Exception as e:
            print(f"[ReplayBuffer] Error calculating quality metrics: {e}")
            return {"error": str(e)}