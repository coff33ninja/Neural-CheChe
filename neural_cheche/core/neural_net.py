"""
Unified neural network architecture for multiple games
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class GameNet(nn.Module):
    """Unified neural network that can play multiple games"""
    
    def __init__(self, input_channels=112, num_actions_chess=4672, num_actions_checkers=1000):
        super(GameNet, self).__init__()
        
        # Shared backbone - ResNet-style architecture
        self.shared_backbone = nn.Sequential(
            nn.Conv2d(input_channels, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
        )
        
        # Residual blocks
        self.residual_blocks = nn.ModuleList([
            self._make_residual_block(256) for _ in range(4)
        ])
        
        # Game-specific policy heads
        self.chess_policy_head = nn.Sequential(
            nn.Conv2d(256, 2, kernel_size=1),
            nn.BatchNorm2d(2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * 8 * 8, num_actions_chess)
        )
        
        self.checkers_policy_head = nn.Sequential(
            nn.Conv2d(256, 2, kernel_size=1),
            nn.BatchNorm2d(2),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * 8 * 8, num_actions_checkers)
        )
        
        # Shared value head
        self.value_head = nn.Sequential(
            nn.Conv2d(256, 1, kernel_size=1),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(8 * 8, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Tanh()
        )
    
    def _make_residual_block(self, channels):
        """Create a residual block"""
        return nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels)
        )
    
    def forward(self, x, game_type):
        """Forward pass through the network"""
        # Shared feature extraction
        x = self.shared_backbone(x)
        
        # Apply residual blocks
        for block in self.residual_blocks:
            residual = x
            x = block(x)
            x = F.relu(x + residual)
        
        # Value prediction (shared)
        value = self.value_head(x)
        
        # Policy prediction (game-specific)
        if game_type == "chess":
            policy = self.chess_policy_head(x)
        elif game_type == "checkers":
            policy = self.checkers_policy_head(x)
        else:
            raise ValueError(f"Unsupported game type: {game_type}")
        
        return F.softmax(policy, dim=1), value
    
    def get_device(self):
        """Get the device this model is on"""
        return next(self.parameters()).device