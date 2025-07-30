"""
AI Agent definitions for the league system
"""

import torch
from torch.optim import Adam
from ..core import GameNet, TrainingManager
from ..utils import safe_device


class AIAgent:
    """Base AI agent class"""
    
    def __init__(self, name, net=None, device=None):
        self.name = name
        self.device = device or safe_device()
        self.net = net or GameNet().to(self.device)
        self.optimizer = Adam(self.net.parameters(), lr=0.001)
        self.training_manager = TrainingManager(self.net, self.optimizer, self.device)
        
        # Statistics
        self.wins = {"chess": 0, "checkers": 0}
        self.games_played = {"chess": 0, "checkers": 0}
        self.total_reward = {"chess": 0.0, "checkers": 0.0}
    
    def get_win_rate(self, game_type):
        """Get win rate for a specific game type"""
        games = self.games_played.get(game_type, 0)
        if games == 0:
            return 0.0
        return self.wins.get(game_type, 0) / games
    
    def record_game_result(self, game_type, won, reward):
        """Record the result of a game"""
        self.games_played[game_type] = self.games_played.get(game_type, 0) + 1
        if won:
            self.wins[game_type] = self.wins.get(game_type, 0) + 1
        self.total_reward[game_type] = self.total_reward.get(game_type, 0) + reward
    
    def get_average_reward(self, game_type):
        """Get average reward for a game type"""
        games = self.games_played.get(game_type, 0)
        if games == 0:
            return 0.0
        return self.total_reward.get(game_type, 0) / games
    
    def copy_weights_from(self, other_agent):
        """Copy neural network weights from another agent"""
        self.net.load_state_dict(other_agent.net.state_dict())
    
    def save_model(self, filepath):
        """Save the agent's model"""
        torch.save({
            'model_state_dict': self.net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'wins': self.wins,
            'games_played': self.games_played,
            'total_reward': self.total_reward,
            'name': self.name
        }, filepath)
    
    def load_model(self, filepath):
        """Load the agent's model"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            self.net.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.wins = checkpoint.get('wins', {"chess": 0, "checkers": 0})
            self.games_played = checkpoint.get('games_played', {"chess": 0, "checkers": 0})
            self.total_reward = checkpoint.get('total_reward', {"chess": 0.0, "checkers": 0.0})
            print(f"[{self.name}] Model loaded from {filepath}")
        except Exception as e:
            print(f"[{self.name}] Error loading model: {e}")
    
    def get_stats(self):
        """Get comprehensive statistics"""
        return {
            'name': self.name,
            'wins': self.wins.copy(),
            'games_played': self.games_played.copy(),
            'win_rates': {
                game: self.get_win_rate(game) 
                for game in ['chess', 'checkers']
            },
            'average_rewards': {
                game: self.get_average_reward(game) 
                for game in ['chess', 'checkers']
            },
            'device': str(self.device)
        }
    
    def __str__(self):
        return f"AIAgent({self.name})"


class ChampionAgent(AIAgent):
    """Champion AI agent - the current best performer"""
    
    def __init__(self, device=None):
        super().__init__("Champion", device=device)
        self.promotion_history = []  # Track when this agent became champion
        self.defense_record = {"wins": 0, "losses": 0}  # Track championship defenses
    
    def promote_from_challenger(self, challenger_agent, generation):
        """Promote this agent from a challenger"""
        self.copy_weights_from(challenger_agent)
        self.promotion_history.append({
            'generation': generation,
            'previous_stats': challenger_agent.get_stats()
        })
        print(f"[Champion] Promoted at generation {generation}")
    
    def record_defense(self, won):
        """Record a championship defense"""
        if won:
            self.defense_record["wins"] += 1
        else:
            self.defense_record["losses"] += 1
    
    def get_defense_rate(self):
        """Get championship defense success rate"""
        total = self.defense_record["wins"] + self.defense_record["losses"]
        if total == 0:
            return 1.0
        return self.defense_record["wins"] / total


class TrainingAgent(AIAgent):
    """Training AI agent - specialized for learning specific aspects"""
    
    def __init__(self, name, specialization=None, device=None):
        super().__init__(name, device=device)
        self.specialization = specialization  # e.g., "opening", "endgame", "tactics"
        self.learning_focus = []  # Track what this agent is learning
        self.training_iterations = 0
    
    def set_learning_focus(self, focus_areas):
        """Set what this agent should focus on learning"""
        self.learning_focus = focus_areas
        print(f"[{self.name}] Learning focus set to: {focus_areas}")
    
    def record_training_iteration(self, loss_info):
        """Record a training iteration"""
        self.training_iterations += 1
        if self.training_iterations % 100 == 0:
            print(f"[{self.name}] Completed {self.training_iterations} training iterations")
    
    def get_training_stats(self):
        """Get training-specific statistics"""
        stats = self.get_stats()
        stats.update({
            'specialization': self.specialization,
            'learning_focus': self.learning_focus,
            'training_iterations': self.training_iterations
        })
        return stats


class WildcardAgent(AIAgent):
    """Wildcard AI agent - fresh, untrained opponent for skill measurement"""
    
    def __init__(self, device=None):
        super().__init__("Wildcard", device=device)
        self.is_fresh = True  # Always starts fresh
        self.baseline_scores = []  # Track performance against this baseline
    
    def reset_to_fresh(self):
        """Reset to completely fresh/random state"""
        # Reinitialize the network with random weights
        self.net = GameNet().to(self.device)
        self.optimizer = Adam(self.net.parameters(), lr=0.001)
        self.training_manager = TrainingManager(self.net, self.optimizer, self.device)
        self.is_fresh = True
        print(f"[{self.name}] Reset to fresh state")
    
    def record_baseline_score(self, opponent_name, score, generation):
        """Record a baseline score against this wildcard"""
        self.baseline_scores.append({
            'opponent': opponent_name,
            'score': score,
            'generation': generation
        })
    
    def get_baseline_trend(self, opponent_name, last_n=5):
        """Get the trend of scores against this wildcard"""
        opponent_scores = [
            entry['score'] for entry in self.baseline_scores 
            if entry['opponent'] == opponent_name
        ]
        
        if len(opponent_scores) < 2:
            return 0.0  # No trend available
        
        recent_scores = opponent_scores[-last_n:]
        if len(recent_scores) < 2:
            return 0.0
        
        # Simple linear trend calculation
        x = list(range(len(recent_scores)))
        y = recent_scores
        
        # Calculate slope
        n = len(x)
        slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        return slope