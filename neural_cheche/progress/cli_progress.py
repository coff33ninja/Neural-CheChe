"""
CLI Progress Tracking with tqdm integration
"""

from typing import Dict, List, Any, Optional
import sys
from datetime import datetime, timedelta

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("⚠️ tqdm not available, using basic progress display")


class CLIProgress:
    """CLI progress tracking with tqdm-style progress bars"""
    
    def __init__(self, total_generations: int):
        self.total_generations = total_generations
        self.current_generation = 0
        
        # Progress bars
        self.generation_bar: Optional[tqdm] = None
        self.phase_bar: Optional[tqdm] = None
        
        # Metrics tracking
        self.current_metrics: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Initialize generation progress bar
        self.create_generation_bar()
    
    def create_generation_bar(self) -> Optional[tqdm]:
        """Create the main generation progress bar"""
        if not TQDM_AVAILABLE:
            print(f"🚀 Starting training for {self.total_generations} generations...")
            return None
        
        try:
            self.generation_bar = tqdm(
                total=self.total_generations,
                desc="🧠 Training Progress",
                unit="gen",
                ncols=100,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                file=sys.stdout
            )
            
            # Add initial metrics display
            self.generation_bar.set_postfix_str("Initializing...")
            
            return self.generation_bar
            
        except Exception as e:
            print(f"⚠️ Failed to create generation bar: {e}")
            return None
    
    def create_phase_bar(self, phase_name: str, total_steps: int) -> Optional[tqdm]:
        """
        Create a progress bar for a specific training phase
        
        Args:
            phase_name: Name of the training phase
            total_steps: Total steps in this phase
            
        Returns:
            tqdm progress bar or None
        """
        if not TQDM_AVAILABLE:
            print(f"📊 Phase: {phase_name} ({total_steps} steps)")
            return None
        
        try:
            # Close existing phase bar if any
            if self.phase_bar:
                self.phase_bar.close()
            
            self.phase_bar = tqdm(
                total=total_steps,
                desc=f"⚡ {phase_name}",
                unit="step",
                ncols=80,
                leave=False,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}]",
                file=sys.stdout
            )
            
            return self.phase_bar
            
        except Exception as e:
            print(f"⚠️ Failed to create phase bar: {e}")
            return None
    
    def update_generation(self, current: int, metrics: Dict[str, Any]) -> None:
        """
        Update generation progress
        
        Args:
            current: Current generation number
            metrics: Training metrics dictionary
        """
        self.current_generation = current
        self.current_metrics = metrics
        
        if TQDM_AVAILABLE and self.generation_bar:
            try:
                # Update progress
                self.generation_bar.n = current
                
                # Create metrics display string
                metrics_str = self._format_metrics(metrics)
                self.generation_bar.set_postfix_str(metrics_str)
                
                # Refresh display
                self.generation_bar.refresh()
                
            except Exception as e:
                print(f"⚠️ Generation update failed: {e}")
        else:
            # Fallback display
            progress_pct = (current / self.total_generations) * 100
            metrics_str = self._format_metrics(metrics)
            print(f"🧠 Generation {current}/{self.total_generations} ({progress_pct:.1f}%) - {metrics_str}")
    
    def update_phase(self, phase: str, progress: float) -> None:
        """
        Update phase progress
        
        Args:
            phase: Phase name
            progress: Progress percentage (0.0 to 1.0)
        """
        if TQDM_AVAILABLE and self.phase_bar:
            try:
                # Update phase bar
                new_n = int(progress * self.phase_bar.total)
                self.phase_bar.n = new_n
                self.phase_bar.set_description(f"⚡ {phase}")
                self.phase_bar.refresh()
                
            except Exception as e:
                print(f"⚠️ Phase update failed: {e}")
        else:
            # Fallback display
            progress_pct = progress * 100
            print(f"⚡ {phase}: {progress_pct:.1f}%")
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update displayed metrics
        
        Args:
            metrics: Dictionary of metrics to display
        """
        self.current_metrics.update(metrics)
        
        if TQDM_AVAILABLE and self.generation_bar:
            try:
                metrics_str = self._format_metrics(self.current_metrics)
                self.generation_bar.set_postfix_str(metrics_str)
                self.generation_bar.refresh()
            except Exception as e:
                print(f"⚠️ Metrics update failed: {e}")
    
    def display_growth_summary(self, historical_data: List[Dict[str, Any]]) -> None:
        """
        Display a summary of generational growth
        
        Args:
            historical_data: List of historical performance data
        """
        if not historical_data:
            return
        
        print("\n" + "="*60)
        print("📈 GENERATIONAL GROWTH SUMMARY")
        print("="*60)
        
        try:
            # Calculate growth metrics
            if len(historical_data) >= 2:
                first_gen = historical_data[0]
                latest_gen = historical_data[-1]
                
                # Win rate improvement
                if 'win_rate' in first_gen and 'win_rate' in latest_gen:
                    win_rate_change = latest_gen['win_rate'] - first_gen['win_rate']
                    print(f"🎯 Win Rate: {first_gen['win_rate']:.1%} → {latest_gen['win_rate']:.1%} ({win_rate_change:+.1%})")
                
                # Training loss improvement
                if 'training_loss' in first_gen and 'training_loss' in latest_gen:
                    loss_change = latest_gen['training_loss'] - first_gen['training_loss']
                    print(f"📉 Training Loss: {first_gen['training_loss']:.4f} → {latest_gen['training_loss']:.4f} ({loss_change:+.4f})")
                
                # Skill improvement
                if 'skill_score' in first_gen and 'skill_score' in latest_gen:
                    skill_change = latest_gen['skill_score'] - first_gen['skill_score']
                    print(f"🧠 Skill Score: {first_gen['skill_score']:.2f} → {latest_gen['skill_score']:.2f} ({skill_change:+.2f})")
            
            # Recent performance
            recent_data = historical_data[-5:]  # Last 5 generations
            if recent_data:
                avg_win_rate = sum(d.get('win_rate', 0) for d in recent_data) / len(recent_data)
                avg_loss = sum(d.get('training_loss', 0) for d in recent_data) / len(recent_data)
                
                print(f"\n📊 Recent Performance (last {len(recent_data)} generations):")
                print(f"   Average Win Rate: {avg_win_rate:.1%}")
                print(f"   Average Loss: {avg_loss:.4f}")
            
            # Training time
            elapsed = datetime.now() - self.start_time
            print(f"\n⏱️ Training Time: {self._format_duration(elapsed)}")
            
            # Estimated completion
            if self.current_generation > 0:
                time_per_gen = elapsed / self.current_generation
                remaining_gens = self.total_generations - self.current_generation
                eta = time_per_gen * remaining_gens
                print(f"🎯 Estimated Completion: {self._format_duration(eta)}")
            
        except Exception as e:
            print(f"⚠️ Error displaying growth summary: {e}")
        
        print("="*60 + "\n")
    
    def close_all_bars(self) -> None:
        """Close all progress bars"""
        if TQDM_AVAILABLE:
            if self.phase_bar:
                self.phase_bar.close()
                self.phase_bar = None
            
            if self.generation_bar:
                self.generation_bar.close()
                self.generation_bar = None
    
    def cleanup(self) -> None:
        """Clean up CLI progress resources"""
        self.close_all_bars()
        
        # Final summary
        elapsed = datetime.now() - self.start_time
        print(f"\n🏁 Training completed in {self._format_duration(elapsed)}")
        print(f"📊 Final generation: {self.current_generation}/{self.total_generations}")
        
        if self.current_metrics:
            print("📈 Final metrics:")
            for key, value in self.current_metrics.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.4f}")
                else:
                    print(f"   {key}: {value}")
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for display"""
        if not metrics:
            return "No metrics"
        
        try:
            # Priority metrics to show
            priority_keys = ['win_rate', 'training_loss', 'games_played', 'skill_score']
            
            formatted_parts = []
            
            for key in priority_keys:
                if key in metrics:
                    value = metrics[key]
                    if key == 'win_rate':
                        formatted_parts.append(f"WR:{value:.1%}")
                    elif key == 'training_loss':
                        formatted_parts.append(f"Loss:{value:.4f}")
                    elif key == 'games_played':
                        formatted_parts.append(f"Games:{value}")
                    elif key == 'skill_score':
                        formatted_parts.append(f"Skill:{value:.2f}")
            
            # Add other metrics if space allows
            other_metrics = {k: v for k, v in metrics.items() if k not in priority_keys}
            if other_metrics and len(formatted_parts) < 3:
                for key, value in list(other_metrics.items())[:2]:
                    if isinstance(value, (int, float)):
                        if isinstance(value, float):
                            formatted_parts.append(f"{key}:{value:.3f}")
                        else:
                            formatted_parts.append(f"{key}:{value}")
            
            return " | ".join(formatted_parts) if formatted_parts else "Training..."
            
        except Exception as e:
            return f"Metrics error: {e}"
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"