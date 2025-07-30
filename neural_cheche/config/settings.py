"""
Configuration settings for Neural CheChe
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class Config:
    """Configuration class for Neural CheChe"""
    
    # Training parameters
    learning_rate: float = 0.001
    batch_size: int = 64
    buffer_capacity: int = 100000
    training_steps_per_generation: int = 50
    
    # Game parameters
    games_per_generation: int = 6
    max_moves_per_game: int = 200
    mcts_simulations: int = 25
    exploration_rate: float = 0.1
    
    # League parameters
    challenger_interval: int = 5
    wildcard_interval: int = 3
    challenger_threshold: float = 0.55
    evaluation_games: int = 20
    
    # Visualization parameters
    enable_visualization: bool = True
    window_width: int = 1240
    window_height: int = 700
    square_size: int = 60
    move_delay: float = 0.1
    
    # System parameters
    device: Optional[str] = None  # Auto-detect if None
    num_parallel_games: int = 1
    save_interval: int = 10
    
    # Advanced parameters
    shared_learning_weight: float = 0.3
    min_exploration_rate: float = 0.01
    exploration_decay: float = 0.995
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'Config':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if self.learning_rate <= 0:
            issues.append("Learning rate must be positive")
        
        if self.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.buffer_capacity <= 0:
            issues.append("Buffer capacity must be positive")
        
        if self.challenger_threshold < 0 or self.challenger_threshold > 1:
            issues.append("Challenger threshold must be between 0 and 1")
        
        if self.exploration_rate < 0 or self.exploration_rate > 1:
            issues.append("Exploration rate must be between 0 and 1")
        
        if self.move_delay < 0:
            issues.append("Move delay cannot be negative")
        
        return issues
    
    def get_display_info(self) -> Dict[str, str]:
        """Get formatted configuration info for display"""
        return {
            "Learning Rate": f"{self.learning_rate:.6f}",
            "Batch Size": str(self.batch_size),
            "Buffer Capacity": f"{self.buffer_capacity:,}",
            "MCTS Simulations": str(self.mcts_simulations),
            "Challenger Threshold": f"{self.challenger_threshold:.1%}",
            "Visualization": "Enabled" if self.enable_visualization else "Disabled",
            "Device": self.device or "Auto-detect"
        }


def load_config(filepath: str = "config.json") -> Config:
    """Load configuration from file"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
            
            config = Config.from_dict(config_dict)
            
            # Validate configuration
            issues = config.validate()
            if issues:
                print("⚠️ Configuration issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                print("Using default values for invalid settings.")
                
                # Create new config with defaults for invalid settings
                default_config = Config()
                for key, value in config_dict.items():
                    if hasattr(default_config, key):
                        try:
                            setattr(config, key, value)
                        except (ValueError, TypeError):
                            print(f"  - Using default for {key}")
            
            print(f"✅ Configuration loaded from {filepath}")
            return config
            
        except Exception as e:
            print(f"❌ Error loading config from {filepath}: {e}")
            print("Using default configuration.")
            return Config()
    else:
        print(f"📝 Config file {filepath} not found. Using defaults.")
        return Config()


def save_config(config: Config, filepath: str = "config.json") -> bool:
    """Save configuration to file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        
        print(f"✅ Configuration saved to {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving config to {filepath}: {e}")
        return False


def create_training_config() -> Config:
    """Create a configuration optimized for training"""
    config = Config()
    
    # Training-focused settings
    config.learning_rate = 0.001
    config.batch_size = 32  # Smaller for stability
    config.training_steps_per_generation = 100
    config.mcts_simulations = 50  # More thorough search
    config.challenger_interval = 3  # More frequent challenges
    config.evaluation_games = 50  # More thorough evaluation
    
    return config


def create_fast_config() -> Config:
    """Create a configuration optimized for speed"""
    config = Config()
    
    # Speed-focused settings
    config.batch_size = 16  # Smaller batches
    config.training_steps_per_generation = 25
    config.mcts_simulations = 10  # Faster search
    config.challenger_interval = 10  # Less frequent challenges
    config.evaluation_games = 10  # Faster evaluation
    config.move_delay = 0.05  # Faster visualization
    
    return config


def create_visualization_config() -> Config:
    """Create a configuration optimized for visualization"""
    config = Config()
    
    # Visualization-focused settings
    config.enable_visualization = True
    config.move_delay = 0.5  # Slower for better viewing
    config.mcts_simulations = 15  # Balanced for responsiveness
    config.window_width = 1400
    config.window_height = 800
    config.square_size = 70  # Larger squares
    
    return config


def get_preset_configs() -> Dict[str, Config]:
    """Get dictionary of preset configurations"""
    return {
        "default": Config(),
        "training": create_training_config(),
        "fast": create_fast_config(),
        "visualization": create_visualization_config()
    }


if __name__ == "__main__":
    # Example usage
    config = Config()
    print("Default configuration:")
    for key, value in config.get_display_info().items():
        print(f"  {key}: {value}")
    
    # Save example config
    save_config(config, "example_config.json")
    
    # Load it back
    loaded_config = load_config("example_config.json")
    print(f"\nLoaded config learning rate: {loaded_config.learning_rate}")