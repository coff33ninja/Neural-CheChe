"""
Training algorithms and utilities
"""

import torch
import torch.nn.functional as F
import numpy as np
from ..utils.gpu_utils import clear_gpu_memory


class TrainingManager:
    """Manages neural network training"""
    
    def __init__(self, net, optimizer, device):
        self.net = net
        self.optimizer = optimizer
        self.device = device
    
    def train_step(self, batch, game_type="chess"):
        """Perform a single training step"""
        try:
            states, policies, values, _ = zip(*batch)
            
            # Convert states to tensor
            states_np = []
            for state in states:
                if hasattr(state, "cpu"):
                    states_np.append(state.cpu().numpy())
                else:
                    states_np.append(state)
            
            states = torch.tensor(np.array(states_np), dtype=torch.float32)
            
            # Move to device
            if self.device.type != "cpu":
                states = states.to(self.device)
            
            # Prepare target policies
            target_policies = []
            for policy in policies:
                if isinstance(policy, dict):
                    policy_tensor = torch.tensor(list(policy.values()), dtype=torch.float32)
                else:
                    policy_tensor = torch.tensor(policy, dtype=torch.float32)
                target_policies.append(policy_tensor)
            
            if self.device.type != "cpu":
                target_policies = [tp.to(self.device) for tp in target_policies]
            
            # Prepare target values
            target_values = torch.tensor(values, dtype=torch.float32).unsqueeze(1)
            if self.device.type != "cpu":
                target_values = target_values.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            if self.device.type == "cuda":
                with torch.cuda.amp.autocast():
                    pred_policies, pred_values = self.net(states, game_type)
            else:
                pred_policies, pred_values = self.net(states, game_type)
            
            # Calculate losses
            policy_loss = sum(
                -torch.sum(target * torch.log(pred + 1e-10))
                for target, pred in zip(target_policies, pred_policies)
            ) / len(batch)
            
            value_loss = F.mse_loss(pred_values, target_values)
            total_loss = policy_loss + value_loss
            
            # Backward pass
            total_loss.backward()
            self.optimizer.step()
            
            loss_value = total_loss.item()
            
            # Clean up GPU memory
            del states, target_policies, target_values, pred_policies, pred_values, total_loss
            clear_gpu_memory()
            
            return {
                "total_loss": loss_value,
                "policy_loss": policy_loss.item() if hasattr(policy_loss, 'item') else 0,
                "value_loss": value_loss.item() if hasattr(value_loss, 'item') else 0
            }
            
        except Exception as e:
            print(f"[TrainingManager] Training step error: {e}")
            clear_gpu_memory()
            return {"total_loss": 0.0, "policy_loss": 0.0, "value_loss": 0.0}
    
    def evaluate_batch(self, batch, game_type="chess"):
        """Evaluate a batch without training"""
        try:
            with torch.no_grad():
                states, policies, values, _ = zip(*batch)
                
                # Convert states
                states_np = []
                for state in states:
                    if hasattr(state, "cpu"):
                        states_np.append(state.cpu().numpy())
                    else:
                        states_np.append(state)
                
                states = torch.tensor(np.array(states_np), dtype=torch.float32)
                if self.device.type != "cpu":
                    states = states.to(self.device)
                
                # Forward pass
                pred_policies, pred_values = self.net(states, game_type)
                
                # Calculate accuracy metrics
                pred_values_np = pred_values.cpu().numpy().flatten()
                target_values_np = np.array(values)
                
                value_accuracy = np.mean(np.abs(pred_values_np - target_values_np))
                
                return {
                    "value_accuracy": value_accuracy,
                    "batch_size": len(batch)
                }
                
        except Exception as e:
            print(f"[TrainingManager] Evaluation error: {e}")
            return {"value_accuracy": 0.0, "batch_size": 0}
    
    def save_checkpoint(self, filepath, generation, additional_info=None):
        """Save training checkpoint"""
        try:
            checkpoint = {
                'model_state_dict': self.net.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'generation': generation,
                'device': str(self.device)
            }
            
            if additional_info:
                checkpoint.update(additional_info)
            
            torch.save(checkpoint, filepath)
            print(f"[TrainingManager] Checkpoint saved to {filepath}")
            
        except Exception as e:
            print(f"[TrainingManager] Error saving checkpoint: {e}")
    
    def load_checkpoint(self, filepath):
        """Load training checkpoint"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            
            self.net.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            generation = checkpoint.get('generation', 0)
            
            print(f"[TrainingManager] Checkpoint loaded from {filepath}, generation {generation}")
            return generation, checkpoint
            
        except Exception as e:
            print(f"[TrainingManager] Error loading checkpoint: {e}")
            return 0, {}
    
    def get_learning_rate(self):
        """Get current learning rate"""
        return self.optimizer.param_groups[0]['lr']
    
    def set_learning_rate(self, lr):
        """Set learning rate"""
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        print(f"[TrainingManager] Learning rate set to {lr}")
    
    def get_model_info(self):
        """Get information about the model"""
        total_params = sum(p.numel() for p in self.net.parameters())
        trainable_params = sum(p.numel() for p in self.net.parameters() if p.requires_grad)
        
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "model_size_mb": total_params * 4 / (1024 * 1024),  # Assuming float32
            "device": str(self.device)
        }