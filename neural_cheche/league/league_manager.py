"""
Main league management system - orchestrates the entire training process
"""

import json
import os

from .agents import ChampionAgent, TrainingAgent, WildcardAgent
from .competition import Competition
from ..core import SharedReplayBuffer
from ..utils import safe_device, get_gpu_info, get_gpu_memory_info, clear_gpu_memory
from ..utils import VisualizationManager
from ..progress import ProgressManager
from ..config import ConfigManager
from ..validation import MoveValidator
from ..history import MoveLogger, BackupManager
from ..error_handling import ErrorHandler, ErrorCategory, ErrorSeverity, RecoveryManager, UserNotifier
from ..error_handling.decorators import handle_errors


class LeagueManager:
    """Main orchestrator for the Neural CheChe training system"""
    
    def __init__(self, config_file=None, config_manager=None, config_dict=None):
        print("🚀 Initializing Neural CheChe League Manager...")
        
        # Configuration management
        if config_manager:
            self.config_manager = config_manager
        elif config_file:
            self.config_manager = ConfigManager(config_file)
        elif config_dict:
            # Create a temporary config manager and override with provided config
            self.config_manager = ConfigManager()
            self._override_config_from_dict(config_dict)
        else:
            # Try to load default config file, fallback to defaults
            default_config_path = 'config/neural_cheche_config.json'
            if os.path.exists(default_config_path):
                self.config_manager = ConfigManager(default_config_path)
            else:
                self.config_manager = ConfigManager()
        
        # Validate configuration
        if not self.config_manager.validate_all_configs():
            print("⚠️ Configuration validation failed, using defaults where possible")
        
        # Legacy config for backward compatibility
        self.config = self._build_legacy_config()
        
        # Device setup
        self.device = safe_device()
        print(f"Device: {get_gpu_info()}")
        print(f"Initial GPU state: {get_gpu_memory_info()}")
        
        # Initialize agents
        self._initialize_agents()
        
        # Training infrastructure
        self.replay_buffer = SharedReplayBuffer(self.config['buffer_capacity'])
        self.competition = Competition()
        
        # Training state
        self.generation = 0
        self.training_stats = []
        self.champion_history = []
        
        # Visualization
        self.visualization_manager = None
        if self.config['enable_visualization']:
            self.visualization_manager = VisualizationManager()
            self.competition.visualization_manager = self.visualization_manager
        
        # Progress tracking
        self.progress_manager = None
        self._initialize_progress_tracking()
        
        # Initialize new enhancement systems
        self._initialize_error_handling_system()
        self._initialize_validation_system()
        self._initialize_history_system()
        
        print("✅ League Manager initialized successfully")
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'learning_rate': 0.001,
            'buffer_capacity': 100000,
            'batch_size': 64,
            'training_steps_per_generation': 50,
            'games_per_generation': 6,
            'challenger_interval': 5,
            'wildcard_interval': 3,
            'challenger_threshold': 0.55,
            'enable_visualization': True,
            'move_delay': 0.1,
            'max_moves_per_game': 200,
            'save_interval': 10,
            # Progress tracking configuration
            'enable_cli_progress': True,
            'enable_gui_progress': True,
            'progress_update_frequency': 0.1,
            'show_detailed_metrics': True
        }
    
    def _initialize_agents(self):
        """Initialize all AI agents"""
        try:
            # Create agents
            self.champion = ChampionAgent(device=self.device)
            self.alpha = TrainingAgent("Alpha", specialization="opening", device=self.device)
            self.beta = TrainingAgent("Beta", specialization="endgame", device=self.device)
            self.wildcard = WildcardAgent(device=self.device)
            
            # Start with champion as baseline for training agents
            self.alpha.copy_weights_from(self.champion)
            self.beta.copy_weights_from(self.champion)
            
            # Set learning focuses
            self.alpha.set_learning_focus(["opening_strategy", "piece_development"])
            self.beta.set_learning_focus(["endgame_technique", "tactical_patterns"])
            
            print("🤖 All agents initialized")
            
        except Exception as e:
            print(f"❌ Error initializing agents: {e}")
            raise
    
    @handle_errors(
        category=ErrorCategory.PROGRESS,
        severity=ErrorSeverity.LOW,
        component="progress_tracking",
        recovery_scenario="progress_display_failed",
        max_retries=1,
        suppress_errors=True
    )
    def _initialize_progress_tracking(self):
        """Initialize progress tracking system"""
        try:
            # Create progress configuration
            progress_config = {
                'enable_cli_progress': self.config.get('enable_cli_progress', True),
                'enable_gui_progress': self.config.get('enable_gui_progress', True),
                'update_frequency': self.config.get('progress_update_frequency', 0.1),
                'show_detailed_metrics': self.config.get('show_detailed_metrics', True)
            }
            
            # Initialize progress manager
            self.progress_manager = ProgressManager(progress_config)
            
            print("📊 Progress tracking initialized")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize progress tracking: {e}")
            self.progress_manager = None
    
    def _override_config_from_dict(self, config_dict):
        """Override configuration manager settings with values from config dictionary"""
        # Update core configuration
        if hasattr(self.config_manager, '_core_config'):
            for key, value in config_dict.items():
                if key in self.config_manager._core_config:
                    self.config_manager._core_config[key] = value
        
        # Update visualization settings if present
        if hasattr(self.config_manager, 'gui') and hasattr(self.config_manager.gui, 'config'):
            gui_keys = ['enable_visualization', 'window_width', 'window_height', 'square_size', 'move_delay']
            for key in gui_keys:
                if key in config_dict:
                    setattr(self.config_manager.gui.config, key, config_dict[key])

    def _build_legacy_config(self):
        """Build legacy configuration dictionary from ConfigManager for backward compatibility"""
        config = {}
        
        # Core configuration
        config.update({
            'learning_rate': self.config_manager.get_core_config('learning_rate', 0.001),
            'buffer_capacity': self.config_manager.get_core_config('buffer_capacity', 100000),
            'batch_size': self.config_manager.get_core_config('batch_size', 64),
            'training_steps_per_generation': self.config_manager.get_core_config('training_steps_per_generation', 50),
            'games_per_generation': self.config_manager.get_core_config('games_per_generation', 6),
            'challenger_interval': self.config_manager.get_core_config('challenger_interval', 5),
            'wildcard_interval': self.config_manager.get_core_config('wildcard_interval', 3),
            'challenger_threshold': self.config_manager.get_core_config('challenger_threshold', 0.55),
            'move_delay': self.config_manager.get_core_config('move_delay', 0.1),
            'max_moves_per_game': self.config_manager.get_core_config('max_moves_per_game', 200),
            'save_interval': self.config_manager.get_core_config('save_interval', 10),
        })
        
        # GUI configuration
        config.update({
            'enable_visualization': self.config_manager.gui.get('enable_visualization', True),
        })
        
        # Progress configuration
        config.update({
            'enable_cli_progress': self.config_manager.progress.get('enable_cli_progress', True),
            'enable_gui_progress': self.config_manager.progress.get('enable_gui_progress', True),
            'progress_update_frequency': self.config_manager.progress.get('update_frequency', 0.1),
            'show_detailed_metrics': self.config_manager.progress.get('show_detailed_metrics', True),
        })
        
        return config
    
    @handle_errors(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.HIGH,
        component="validation_system",
        recovery_scenario="validation_timeout",
        max_retries=2
    )
    def _initialize_validation_system(self):
        """Initialize move validation system"""
        try:
            if self.config_manager.validation.is_validation_enabled():
                # Initialize validators for different game types
                self.chess_validator = MoveValidator("chess", 
                    log_violations=self.config_manager.validation.get('log_violations', True))
                self.checkers_validator = MoveValidator("checkers", 
                    log_violations=self.config_manager.validation.get('log_violations', True))
                
                # Add validation to competition
                self.competition.set_validators({
                    'chess': self.chess_validator,
                    'checkers': self.checkers_validator
                })
                
                print("🛡️ Move validation system initialized")
            else:
                self.chess_validator = None
                self.checkers_validator = None
                print("⚠️ Move validation disabled by configuration")
                
        except Exception as e:
            print(f"⚠️ Failed to initialize validation system: {e}")
            self.chess_validator = None
            self.checkers_validator = None
            if not self.config_manager.error_handling.should_continue_on_failure():
                raise
    
    @handle_errors(
        category=ErrorCategory.HISTORY,
        severity=ErrorSeverity.MEDIUM,
        component="history_system",
        recovery_scenario="history_logging_failed",
        max_retries=2
    )
    def _initialize_history_system(self):
        """Initialize move logging and backup system"""
        try:
            if self.config_manager.history.is_logging_enabled():
                # Initialize move logger
                self.move_logger = MoveLogger(
                    backup_directory=self.config_manager.history.get('backup_directory', 'logs/moves')
                )
                
                # Initialize backup manager
                self.backup_manager = BackupManager(
                    base_directory=self.config_manager.history.get('backup_directory', 'backups')
                )
                # Set compression after initialization
                self.backup_manager.compress_backups = self.config_manager.history.get('compress_backups', True)
                
                # Add history tracking to competition
                self.competition.set_history_managers(self.move_logger, self.backup_manager)
                
                print("📝 History and backup system initialized")
            else:
                self.move_logger = None
                self.backup_manager = None
                print("⚠️ History logging disabled by configuration")
                
        except Exception as e:
            print(f"⚠️ Failed to initialize history system: {e}")
            self.move_logger = None
            self.backup_manager = None
            if not self.config_manager.error_handling.should_continue_on_failure():
                raise
    
    def _initialize_error_handling_system(self):
        """Initialize comprehensive error handling system"""
        try:
            # Initialize error handler
            error_config = {
                'log_errors': self.config_manager.error_handling.get('log_errors', True),
                'log_file': self.config_manager.error_handling.get('error_log_path', 'logs/errors.log'),
                'enable_recovery': self.config_manager.error_handling.get('auto_recovery_enabled', True),
                'max_retry_attempts': self.config_manager.error_handling.get('max_retry_attempts', 3),
                'continue_on_failure': self.config_manager.error_handling.should_continue_on_failure(),
                'graceful_degradation': self.config_manager.error_handling.should_use_graceful_degradation(),
                'notify_user': self.config_manager.error_handling.get('notify_user_on_error', True)
            }
            
            self.error_handler = ErrorHandler(error_config)
            self.recovery_manager = RecoveryManager(error_config)
            self.user_notifier = UserNotifier(error_config)
            
            # Register recovery callbacks
            self._register_recovery_callbacks()
            
            print("🔧 Comprehensive error handling system initialized")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize error handling system: {e}")
            # Create minimal error handling if full system fails
            self.error_handler = None
            self.recovery_manager = None
            self.user_notifier = None
    
    def _register_recovery_callbacks(self):
        """Register recovery callbacks for common scenarios"""
        if not self.error_handler or not self.recovery_manager:
            return
        
        # Register configuration recovery
        def config_recovery_callback(error_info):
            try:
                self.config_manager.reset_to_defaults()
                return True
            except Exception:
                return False
        
        self.error_handler.register_recovery_callback(
            ErrorCategory.CONFIGURATION,
            config_recovery_callback
        )
        
        # Register GUI recovery
        def gui_recovery_callback(error_info):
            try:
                # Disable GUI and continue with CLI
                self.config_manager.gui.set('enable_visualization', False)
                if self.visualization_manager:
                    self.visualization_manager = None
                return True
            except Exception:
                return False
        
        self.error_handler.register_recovery_callback(
            ErrorCategory.GUI,
            gui_recovery_callback
        )
    
    def get_system_status(self):
        """Get status of all enhancement systems"""
        return {
            'validation': {
                'enabled': self.config_manager.validation.is_validation_enabled(),
                'chess_validator': self.chess_validator is not None,
                'checkers_validator': self.checkers_validator is not None
            },
            'progress': {
                'enabled': self.config_manager.progress.is_progress_enabled(),
                'cli_enabled': self.config_manager.progress.should_show_cli_progress(),
                'gui_enabled': self.config_manager.progress.should_show_gui_progress(),
                'manager_initialized': self.progress_manager is not None
            },
            'history': {
                'enabled': self.config_manager.history.is_logging_enabled(),
                'move_logger': self.move_logger is not None,
                'backup_manager': self.backup_manager is not None
            },
            'gui': {
                'enabled': self.config_manager.gui.is_visualization_enabled(),
                'visualization_manager': self.visualization_manager is not None
            },
            'error_handling': {
                'enabled': self.error_handler is not None,
                'graceful_degradation': self.config_manager.error_handling.should_use_graceful_degradation(),
                'continue_on_failure': self.config_manager.error_handling.should_continue_on_failure(),
                'recovery_manager': self.recovery_manager is not None,
                'user_notifier': self.user_notifier is not None
            }
        }
    
    def save_configuration(self, filepath=None):
        """Save current configuration to file"""
        try:
            self.config_manager.save_to_file(filepath)
            print("✅ Configuration saved successfully")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def get_error_statistics(self):
        """Get comprehensive error statistics"""
        if not self.error_handler:
            return {'error': 'Error handling system not initialized'}
        
        stats = {
            'error_handler': self.error_handler.get_error_statistics(),
            'recovery_manager': self.recovery_manager.get_recovery_statistics() if self.recovery_manager else {},
            'user_notifier': self.user_notifier.get_notification_statistics() if self.user_notifier else {}
        }
        
        return stats
    
    def clear_error_history(self):
        """Clear all error history"""
        if self.error_handler:
            self.error_handler.clear_error_history()
        if self.recovery_manager:
            self.recovery_manager.clear_recovery_history()
        if self.user_notifier:
            self.user_notifier.clear_notification_history()
        print("🧹 All error history cleared")
    
    @handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.CRITICAL,
        component="training_loop",
        max_retries=1
    )
    def run_training(self, num_generations=100):
        """Run the main training loop"""
        print(f"🎯 Starting training for {num_generations} generations")
        
        # Initialize progress tracking
        if self.progress_manager:
            self.progress_manager.initialize_cli_progress(num_generations)
            if self.visualization_manager:
                self.progress_manager.initialize_gui_progress(self.visualization_manager)
        
        try:
            for gen in range(num_generations):
                self.generation = gen
                print(f"\n🔄 Generation {gen + 1}/{num_generations}")
                
                # Update visualization
                if self.visualization_manager:
                    self.visualization_manager.update_window_title(
                        gen + 1, "Training", "Generation Start"
                    )
                
                # Phase 1: Game Generation
                self._run_game_generation_with_progress()
                
                # Phase 2: AI Strategy Discussion (Training)
                self._run_training_phase_with_progress()
                
                # Phase 3: Challenger System (every N generations)
                if (gen + 1) % self.config['challenger_interval'] == 0:
                    self._run_challenger_phase_with_progress()
                
                # Phase 4: Wildcard Challenge (every N generations)
                if (gen + 1) % self.config['wildcard_interval'] == 0:
                    self._run_wildcard_phase_with_progress()
                
                # Update generation progress
                self._update_generation_progress(gen + 1)
                
                # Save progress
                if (gen + 1) % self.config['save_interval'] == 0:
                    self._save_progress()
                
                # Display statistics
                self._display_generation_stats()
                
                # Check for early stopping or user interruption
                if self.visualization_manager and not self.visualization_manager.process_events():
                    print("🚪 Training interrupted by user")
                    break
        
        except KeyboardInterrupt:
            print("\n⏹️ Training interrupted by user")
        except Exception as e:
            print(f"❌ Training error: {e}")
        finally:
            self._cleanup()
    
    def _run_game_generation(self):
        """Phase 1: Generate games for training data"""
        print("🎮 Phase 1: Game Generation")
        
        games_config = [
            (self.champion, self.champion, "chess", "Champion self-play"),
            (self.alpha, self.beta, "chess", "Alpha vs Beta chess"),
            (self.beta, self.alpha, "chess", "Beta vs Alpha chess"),
            (self.champion, self.champion, "checkers", "Champion self-play checkers"),
            (self.alpha, self.beta, "checkers", "Alpha vs Beta checkers"),
            (self.beta, self.alpha, "checkers", "Beta vs Alpha checkers")
        ]
        
        total_experiences = 0
        
        for agent1, agent2, game_type, description in games_config:
            print(f"  🎯 {description}")
            
            experiences, reward = self.competition.play_match(
                agent1, agent2, game_type,
                visualize=self.config['enable_visualization'],
                replay_buffer=self.replay_buffer
            )
            
            total_experiences += len(experiences)
            print(f"    📊 Generated {len(experiences)} experiences, reward: {reward:.3f}")
        
        print(f"✅ Game generation complete. Total experiences: {total_experiences}")
    
    def _run_training_phase(self):
        """Phase 2: AI Strategy Discussion (Training)"""
        print("🧠 Phase 2: AI Strategy Discussion (Training)")
        
        if len(self.replay_buffer) < self.config['batch_size']:
            print("  ⚠️ Not enough experiences for training")
            return
        
        # Train each agent
        agents_to_train = [self.champion, self.alpha, self.beta]
        training_results = {}
        
        for agent in agents_to_train:
            print(f"  🎓 Training {agent.name}...")
            
            total_loss = 0
            for step in range(self.config['training_steps_per_generation']):
                # Sample batch
                batch = self.replay_buffer.sample(self.config['batch_size'])
                
                # Train on chess and checkers data
                chess_batch = [exp for exp in batch if 'chess' in str(exp)]
                checkers_batch = [exp for exp in batch if 'checkers' in str(exp)]
                
                step_loss = 0
                if chess_batch:
                    loss_info = agent.training_manager.train_step(chess_batch, "chess")
                    step_loss += loss_info['total_loss']
                
                if checkers_batch:
                    loss_info = agent.training_manager.train_step(checkers_batch, "checkers")
                    step_loss += loss_info['total_loss']
                
                total_loss += step_loss
                agent.record_training_iteration({'loss': step_loss})
            
            avg_loss = total_loss / self.config['training_steps_per_generation']
            training_results[agent.name] = avg_loss
            print(f"    📈 Average loss: {avg_loss:.4f}")
        
        print("✅ Training phase complete")
        return training_results
    
    def _run_challenger_phase(self):
        """Phase 3: Challenger System"""
        print("⚔️ Phase 3: Challenger System")
        
        # Create challenger from best training agent
        best_agent = self._select_best_training_agent()
        print(f"  🏆 Selected {best_agent.name} as challenger")
        
        # Evaluate challenger against champion
        win_rate = self.competition.evaluate_agents(
            best_agent, self.champion, 
            ["chess", "checkers"], 
            num_games=20
        )
        
        print(f"  📊 Challenger win rate: {win_rate:.2%}")
        
        # Promote if above threshold
        if win_rate > self.config['challenger_threshold']:
            print(f"  👑 Promoting {best_agent.name} to Champion!")
            self.champion.promote_from_challenger(best_agent, self.generation)
            
            # Update training agents with new champion knowledge
            self.alpha.copy_weights_from(self.champion)
            self.beta.copy_weights_from(self.champion)
            
            # Record in history
            self.champion_history.append({
                'generation': self.generation,
                'previous_champion': 'Previous',
                'new_champion': best_agent.name,
                'win_rate': win_rate
            })
        else:
            print("  🛡️ Champion defended successfully")
            self.champion.record_defense(True)
    
    def _run_wildcard_phase(self):
        """Phase 4: Wildcard Challenge"""
        print("🎲 Phase 4: Wildcard Challenge")
        
        # Reset wildcard to fresh state
        self.wildcard.reset_to_fresh()
        
        # Test champion against fresh AI
        win_rate = self.competition.evaluate_agents(
            self.champion, self.wildcard,
            ["chess", "checkers"],
            num_games=10
        )
        
        print(f"  📊 Champion vs Wildcard: {win_rate:.2%}")
        
        # Record baseline score
        self.wildcard.record_baseline_score(
            self.champion.name, win_rate, self.generation
        )
        
        # Analyze improvement trend
        trend = self.wildcard.get_baseline_trend(self.champion.name)
        print(f"  📈 Improvement trend: {trend:.4f}")
    
    def _select_best_training_agent(self):
        """Select the best performing training agent"""
        # Simple selection based on win rates
        alpha_score = (
            self.alpha.get_win_rate("chess") + 
            self.alpha.get_win_rate("checkers")
        ) / 2
        
        beta_score = (
            self.beta.get_win_rate("chess") + 
            self.beta.get_win_rate("checkers")
        ) / 2
        
        return self.alpha if alpha_score > beta_score else self.beta
    
    @handle_errors(
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.MEDIUM,
        component="save_progress",
        recovery_scenario="file_not_found",
        max_retries=2,
        suppress_errors=True
    )
    def _save_progress(self):
        """Save training progress"""
        print("💾 Saving progress...")
        
        try:
            # Save models with error handling for each
            try:
                self.champion.save_model(f"champion_gen_{self.generation}.pth")
            except Exception as e:
                if self.error_handler:
                    self.error_handler.handle_error(
                        error=e,
                        category=ErrorCategory.FILE_IO,
                        severity=ErrorSeverity.MEDIUM,
                        component="LeagueManager",
                        context={"operation": "save_champion_model", "generation": self.generation}
                    )
            
            try:
                self.alpha.save_model(f"alpha_gen_{self.generation}.pth")
            except Exception as e:
                if self.error_handler:
                    self.error_handler.handle_error(
                        error=e,
                        category=ErrorCategory.FILE_IO,
                        severity=ErrorSeverity.MEDIUM,
                        component="LeagueManager",
                        context={"operation": "save_alpha_model", "generation": self.generation}
                    )
            
            try:
                self.beta.save_model(f"beta_gen_{self.generation}.pth")
            except Exception as e:
                if self.error_handler:
                    self.error_handler.handle_error(
                        error=e,
                        category=ErrorCategory.FILE_IO,
                        severity=ErrorSeverity.MEDIUM,
                        component="LeagueManager",
                        context={"operation": "save_beta_model", "generation": self.generation}
                    )
            
            # Save training statistics
            stats = {
                'generation': self.generation,
                'champion_history': self.champion_history,
                'buffer_stats': self.replay_buffer.get_statistics(),
                'agent_stats': {
                    'champion': self.champion.get_stats(),
                    'alpha': self.alpha.get_training_stats(),
                    'beta': self.beta.get_training_stats()
                },
                'competition_stats': self.competition.get_match_statistics()
            }
            
            with open(f"training_stats_gen_{self.generation}.json", 'w') as f:
                json.dump(stats, f, indent=2)
            
            print("✅ Progress saved")
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.FILE_IO,
                    severity=ErrorSeverity.MEDIUM,
                    component="LeagueManager",
                    context={"operation": "save_progress", "generation": self.generation}
                )
            else:
                print(f"❌ Error saving progress: {e}")
    
    def _display_generation_stats(self):
        """Display statistics for the current generation"""
        print(f"\n📊 Generation {self.generation} Statistics:")
        print(f"  Buffer size: {len(self.replay_buffer)}")
        print(f"  Champion defenses: {self.champion.defense_record}")
        print(f"  Alpha stats: W-{self.alpha.wins} | Games-{self.alpha.games_played}")
        print(f"  Beta stats: W-{self.beta.wins} | Games-{self.beta.games_played}")
        print(f"  GPU Memory: {get_gpu_memory_info()}")
        
        # Update visualization if available
        if self.visualization_manager:
            self.visualization_manager.clear_screen()
            
            # Display generation info
            self.visualization_manager.display_generation_info(
                self.generation, "Training Complete",
                {'alpha': self.alpha.wins, 'beta': self.beta.wins}
            )
            
            # Display training stats
            buffer_stats = self.replay_buffer.get_statistics()
            training_stats = {
                'buffer_size': len(self.replay_buffer),
                'mean_reward': buffer_stats.get('mean_reward', 0),
                'gpu_memory': get_gpu_memory_info()
            }
            self.visualization_manager.display_training_stats(training_stats)
            
            # Display network info
            net_info = self.champion.training_manager.get_model_info()
            net_info['learning_rate'] = self.champion.training_manager.get_learning_rate()
            self.visualization_manager.display_network_info(net_info)
            
            self.visualization_manager.refresh_display()
    
    def _cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        # Clear GPU memory
        clear_gpu_memory()
        
        # Close visualization
        if self.visualization_manager:
            self.visualization_manager.cleanup()
        
        # Close progress tracking
        if self.progress_manager:
            self.progress_manager.cleanup()
        
        print("✅ Cleanup complete")
    
    def load_checkpoint(self, generation):
        """Load training state from a checkpoint"""
        try:
            # Load models
            self.champion.load_model(f"champion_gen_{generation}.pth")
            self.alpha.load_model(f"alpha_gen_{generation}.pth")
            self.beta.load_model(f"beta_gen_{generation}.pth")
            
            # Load statistics
            with open(f"training_stats_gen_{generation}.json", 'r') as f:
                stats = json.load(f)
            
            self.generation = stats['generation']
            self.champion_history = stats['champion_history']
            
            print(f"✅ Checkpoint loaded from generation {generation}")
            
        except Exception as e:
            print(f"❌ Error loading checkpoint: {e}")
    
    def get_training_summary(self):
        """Get a summary of the training progress"""
        return {
            'current_generation': self.generation,
            'total_champions': len(self.champion_history),
            'buffer_utilization': len(self.replay_buffer) / self.config['buffer_capacity'],
            'champion_defense_rate': self.champion.get_defense_rate(),
            'alpha_performance': self.alpha.get_stats(),
            'beta_performance': self.beta.get_stats(),
            'recent_matches': len(self.competition.match_history),
            'device_info': str(self.device)
        }
    
    # Progress-enhanced phase methods
    @handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.HIGH,
        component="game_generation",
        recovery_scenario="training_step_failed",
        max_retries=2
    )
    def _run_game_generation_with_progress(self):
        """Phase 1: Generate games for training data with progress tracking"""
        phase_name = "Game Generation"
        print(f"🎮 Phase 1: {phase_name}")
        
        # Update phase progress
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.0)
        
        games_config = [
            (self.champion, self.champion, "chess", "Champion self-play"),
            (self.alpha, self.beta, "chess", "Alpha vs Beta chess"),
            (self.beta, self.alpha, "chess", "Beta vs Alpha chess"),
            (self.champion, self.champion, "checkers", "Champion self-play checkers"),
            (self.alpha, self.beta, "checkers", "Alpha vs Beta checkers"),
            (self.beta, self.alpha, "checkers", "Beta vs Alpha checkers")
        ]
        
        total_experiences = 0
        total_games = len(games_config)
        
        for i, (agent1, agent2, game_type, description) in enumerate(games_config):
            try:
                print(f"  🎯 {description}")
                
                # Update progress
                if self.progress_manager:
                    progress = (i + 0.5) / total_games
                    self.progress_manager.update_phase_progress(phase_name, progress)
                
                experiences, reward = self.competition.play_match(
                    agent1, agent2, game_type,
                    visualize=self.config['enable_visualization'],
                    replay_buffer=self.replay_buffer,
                    generation=self.generation
                )
                
                total_experiences += len(experiences)
                print(f"    📊 Generated {len(experiences)} experiences, reward: {reward:.3f}")
                
            except Exception as e:
                if self.error_handler:
                    self.error_handler.handle_error(
                        error=e,
                        category=ErrorCategory.TRAINING,
                        severity=ErrorSeverity.HIGH,
                        component="LeagueManager",
                        context={
                            "operation": "game_generation",
                            "game_type": game_type,
                            "description": description,
                            "game_index": i
                        }
                    )
                
                # Continue with next game if this one fails
                if self.config_manager.error_handling.should_continue_on_failure():
                    print(f"⚠️ Skipping failed game: {description}")
                    continue
                else:
                    raise
        
        # Complete phase
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 1.0)
        
        print(f"✅ Game generation complete. Total experiences: {total_experiences}")
    
    @handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.HIGH,
        component="training_phase",
        recovery_scenario="training_step_failed",
        max_retries=2
    )
    def _run_training_phase_with_progress(self):
        """Phase 2: AI Strategy Discussion (Training) with progress tracking"""
        phase_name = "AI Training"
        print(f"🧠 Phase 2: {phase_name}")
        
        # Update phase progress
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.0)
        
        if len(self.replay_buffer) < self.config['batch_size']:
            print("  ⚠️ Not enough experiences for training")
            if self.progress_manager:
                self.progress_manager.update_phase_progress(phase_name, 1.0)
            return
        
        # Train each agent
        agents_to_train = [self.champion, self.alpha, self.beta]
        training_results = {}
        total_agents = len(agents_to_train)
        
        for agent_idx, agent in enumerate(agents_to_train):
            print(f"  🎓 Training {agent.name}...")
            
            # Update progress for current agent
            if self.progress_manager:
                base_progress = agent_idx / total_agents
                self.progress_manager.update_phase_progress(phase_name, base_progress)
            
            total_loss = 0
            training_steps = self.config['training_steps_per_generation']
            
            for step in range(training_steps):
                # Update sub-progress
                if self.progress_manager:
                    step_progress = base_progress + (step / training_steps) / total_agents
                    self.progress_manager.update_phase_progress(phase_name, step_progress)
                
                # Sample batch
                batch = self.replay_buffer.sample(self.config['batch_size'])
                
                # Train on chess and checkers data
                chess_batch = [exp for exp in batch if 'chess' in str(exp)]
                checkers_batch = [exp for exp in batch if 'checkers' in str(exp)]
                
                step_loss = 0
                if chess_batch:
                    loss_info = agent.training_manager.train_step(chess_batch, "chess")
                    step_loss += loss_info['total_loss']
                
                if checkers_batch:
                    loss_info = agent.training_manager.train_step(checkers_batch, "checkers")
                    step_loss += loss_info['total_loss']
                
                total_loss += step_loss
                agent.record_training_iteration({'loss': step_loss})
            
            avg_loss = total_loss / training_steps
            training_results[agent.name] = avg_loss
            print(f"    📈 Average loss: {avg_loss:.4f}")
        
        # Complete phase
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 1.0)
        
        print("✅ Training phase complete")
        return training_results
    
    @handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.MEDIUM,
        component="challenger_phase",
        recovery_scenario="training_step_failed",
        max_retries=1
    )
    def _run_challenger_phase_with_progress(self):
        """Phase 3: Challenger System with progress tracking"""
        phase_name = "Challenger System"
        print(f"⚔️ Phase 3: {phase_name}")
        
        # Update phase progress
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.0)
        
        # Create challenger from best training agent
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.2)
        
        best_agent = self._select_best_training_agent()
        print(f"  🏆 Selected {best_agent.name} as challenger")
        
        # Evaluate challenger against champion
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.5)
        
        win_rate = self.competition.evaluate_agents(
            best_agent, self.champion, 
            ["chess", "checkers"], 
            num_games=20
        )
        
        print(f"  📊 Challenger win rate: {win_rate:.2%}")
        
        # Promote if above threshold
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.8)
        
        if win_rate > self.config['challenger_threshold']:
            print(f"  👑 Promoting {best_agent.name} to Champion!")
            self.champion.promote_from_challenger(best_agent, self.generation)
            
            # Update training agents with new champion knowledge
            self.alpha.copy_weights_from(self.champion)
            self.beta.copy_weights_from(self.champion)
            
            # Record in history
            self.champion_history.append({
                'generation': self.generation,
                'previous_champion': 'Previous',
                'new_champion': best_agent.name,
                'win_rate': win_rate
            })
        else:
            print("  🛡️ Champion defended successfully")
            self.champion.record_defense(True)
        
        # Complete phase
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 1.0)
    
    @handle_errors(
        category=ErrorCategory.TRAINING,
        severity=ErrorSeverity.MEDIUM,
        component="wildcard_phase",
        recovery_scenario="training_step_failed",
        max_retries=1
    )
    def _run_wildcard_phase_with_progress(self):
        """Phase 4: Wildcard Challenge with progress tracking"""
        phase_name = "Wildcard Challenge"
        print(f"🎲 Phase 4: {phase_name}")
        
        # Update phase progress
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.0)
        
        # Reset wildcard to fresh state
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.3)
        
        self.wildcard.reset_to_fresh()
        
        # Test champion against fresh AI
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 0.7)
        
        win_rate = self.competition.evaluate_agents(
            self.champion, self.wildcard,
            ["chess", "checkers"],
            num_games=10
        )
        
        print(f"  📊 Champion vs Wildcard: {win_rate:.2%}")
        
        # Record baseline score
        self.wildcard.record_baseline_score(
            self.champion.name, win_rate, self.generation
        )
        
        # Analyze improvement trend
        trend = self.wildcard.get_baseline_trend(self.champion.name)
        print(f"  📈 Improvement trend: {trend:.4f}")
        
        # Complete phase
        if self.progress_manager:
            self.progress_manager.update_phase_progress(phase_name, 1.0)
    
    @handle_errors(
        category=ErrorCategory.PROGRESS,
        severity=ErrorSeverity.LOW,
        component="generation_progress_update",
        recovery_scenario="progress_display_failed",
        max_retries=1,
        suppress_errors=True
    )
    def _update_generation_progress(self, generation: int):
        """Update overall generation progress with metrics"""
        if not self.progress_manager:
            return
        
        try:
            # Calculate current metrics
            metrics = {
                'win_rate': self._calculate_current_win_rate(),
                'training_loss': self._calculate_average_training_loss(),
                'games_played': len(self.competition.match_history),
                'buffer_utilization': len(self.replay_buffer) / self.config['buffer_capacity'],
                'champion_defenses': len([h for h in self.champion_history if h.get('win_rate', 0) <= self.config['challenger_threshold']]),
                'skill_score': self._calculate_skill_score()
            }
            
            # Update progress manager
            self.progress_manager.update_generation_progress(generation, metrics)
            
            # Display generational growth every 5 generations
            if generation % 5 == 0 and generation > 0:
                historical_data = self._get_historical_performance_data()
                self.progress_manager.display_generational_growth(historical_data)
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    error=e,
                    category=ErrorCategory.PROGRESS,
                    severity=ErrorSeverity.LOW,
                    component="LeagueManager",
                    context={"operation": "update_generation_progress", "generation": generation}
                )
            else:
                print(f"⚠️ Error updating generation progress: {e}")
    
    def _calculate_current_win_rate(self) -> float:
        """Calculate current overall win rate"""
        try:
            if not self.competition.match_history:
                return 0.0
            
            recent_matches = self.competition.match_history[-20:]  # Last 20 matches
            wins = sum(1 for match in recent_matches if match.get('winner') in ['Alpha', 'Beta', 'Champion'])
            return wins / len(recent_matches) if recent_matches else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_average_training_loss(self) -> float:
        """Calculate average training loss across all agents"""
        try:
            losses = []
            for agent in [self.champion, self.alpha, self.beta]:
                if hasattr(agent, 'training_manager') and hasattr(agent.training_manager, 'get_recent_loss'):
                    loss = agent.training_manager.get_recent_loss()
                    if loss is not None:
                        losses.append(loss)
            
            return sum(losses) / len(losses) if losses else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_skill_score(self) -> float:
        """Calculate a composite skill score"""
        try:
            # Simple skill score based on win rate and champion stability
            win_rate = self._calculate_current_win_rate()
            champion_stability = 1.0 - (len(self.champion_history) / max(1, self.generation))
            
            return (win_rate * 0.7 + champion_stability * 0.3) * 100
            
        except Exception:
            return 0.0
    
    def _get_historical_performance_data(self) -> list:
        """Get historical performance data for growth analysis"""
        try:
            # Return recent generation data
            historical_data = []
            
            # Add data points from champion history
            for i, champion_data in enumerate(self.champion_history[-10:]):  # Last 10 champions
                historical_data.append({
                    'generation': champion_data.get('generation', i),
                    'win_rate': champion_data.get('win_rate', 0.5),
                    'champion': champion_data.get('new_champion', 'Unknown'),
                    'skill_score': self._calculate_skill_score()
                })
            
            return historical_data
            
        except Exception as e:
            print(f"⚠️ Error getting historical data: {e}")
            return []