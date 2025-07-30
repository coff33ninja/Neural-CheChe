#!/usr/bin/env python3
"""
Neural CheChe: AI vs AI Training System
Main entry point for the modular training system
"""

import argparse
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neural_cheche import LeagueManager, Config, load_config, save_config
from neural_cheche.config import get_preset_configs
from neural_cheche.utils import get_gpu_info, get_gpu_memory_info


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Neural CheChe: AI vs AI Training System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with default settings
  python main.py --config training       # Use training preset
  python main.py --generations 50        # Run for 50 generations
  python main.py --no-viz               # Run without visualization
  python main.py --load-checkpoint 10   # Resume from generation 10
        """
    )
    
    # Configuration options
    parser.add_argument(
        '--config', 
        choices=['default', 'training', 'fast', 'visualization'],
        default='default',
        help='Configuration preset to use'
    )
    
    parser.add_argument(
        '--config-file',
        type=str,
        help='Path to custom configuration file'
    )
    
    # Training options
    parser.add_argument(
        '--generations',
        type=int,
        default=100,
        help='Number of generations to train (default: 100)'
    )
    
    parser.add_argument(
        '--load-checkpoint',
        type=int,
        help='Load from checkpoint at specified generation'
    )
    
    # Visualization options
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization'
    )
    
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Use fast training settings'
    )
    
    # System options
    parser.add_argument(
        '--device',
        choices=['auto', 'cpu', 'cuda', 'mps'],
        default='auto',
        help='Device to use for training'
    )
    
    parser.add_argument(
        '--save-config',
        type=str,
        help='Save current configuration to file and exit'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show system information and exit'
    )
    
    args = parser.parse_args()
    
    # Show system info if requested
    if args.info:
        show_system_info()
        return
    
    # Load configuration
    config = load_configuration(args)
    
    # Save config if requested
    if args.save_config:
        save_config(config, args.save_config)
        print(f"Configuration saved to {args.save_config}")
        return
    
    # Apply command line overrides
    apply_cli_overrides(config, args)
    
    # Display startup information
    display_startup_info(config, args)
    
    try:
        # Initialize and run training
        league_manager = LeagueManager(config.to_dict())
        
        # Load checkpoint if requested
        if args.load_checkpoint:
            league_manager.load_checkpoint(args.load_checkpoint)
        
        # Run training
        league_manager.run_training(args.generations)
        
        # Display final summary
        display_final_summary(league_manager)
        
    except KeyboardInterrupt:
        print("\n⏹️ Training interrupted by user")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def load_configuration(args):
    """Load configuration based on arguments"""
    if args.config_file:
        # Load from custom file
        config = load_config(args.config_file)
    else:
        # Load from preset
        presets = get_preset_configs()
        config = presets.get(args.config, Config())
    
    return config


def apply_cli_overrides(config, args):
    """Apply command line argument overrides to config"""
    if args.no_viz:
        config.enable_visualization = False
    
    if args.fast:
        config.mcts_simulations = 10
        config.training_steps_per_generation = 25
        config.move_delay = 0.05
    
    if args.device != 'auto':
        config.device = args.device


def show_system_info():
    """Display system information"""
    print("🖥️ Neural CheChe System Information")
    print("=" * 50)
    print(f"GPU Info: {get_gpu_info()}")
    print(f"Memory Info: {get_gpu_memory_info()}")
    
    # Check dependencies
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
    except ImportError:
        print("❌ PyTorch not installed")
    
    import importlib.util
    
    # Check dependencies using importlib.util.find_spec
    if importlib.util.find_spec("chess"):
        print("python-chess available: ✅")
    else:
        print("❌ python-chess not installed")
    
    if importlib.util.find_spec("draughts"):
        print("draughts available: ✅")
    else:
        print("❌ draughts not installed")
    
    if importlib.util.find_spec("pygame"):
        print("pygame available: ✅")
    else:
        print("❌ pygame not installed")


def display_startup_info(config, args):
    """Display startup information"""
    print("🚀 Neural CheChe: AI vs AI Training System")
    print("=" * 50)
    print(f"Configuration: {args.config}")
    print(f"Generations: {args.generations}")
    print(f"Visualization: {'Enabled' if config.enable_visualization else 'Disabled'}")
    print(f"Device: {config.device or 'Auto-detect'}")
    
    if args.load_checkpoint:
        print(f"Loading from checkpoint: Generation {args.load_checkpoint}")
    
    print("\n📊 Configuration Details:")
    for key, value in config.get_display_info().items():
        print(f"  {key}: {value}")
    
    print(f"\n🖥️ System: {get_gpu_info()}")
    print("=" * 50)


def display_final_summary(league_manager):
    """Display final training summary"""
    summary = league_manager.get_training_summary()
    
    print("\n🏁 Training Complete!")
    print("=" * 50)
    print(f"Final Generation: {summary['current_generation']}")
    print(f"Total Champions: {summary['total_champions']}")
    print(f"Buffer Utilization: {summary['buffer_utilization']:.1%}")
    print(f"Champion Defense Rate: {summary['champion_defense_rate']:.1%}")
    print(f"Total Matches Played: {summary['recent_matches']}")
    
    print("\n🤖 Agent Performance:")
    alpha_stats = summary['alpha_performance']
    beta_stats = summary['beta_performance']
    
    print(f"Alpha: {alpha_stats['wins']} wins in {alpha_stats['games_played']} games")
    print(f"Beta: {beta_stats['wins']} wins in {beta_stats['games_played']} games")
    
    print("\n💾 Models and logs saved to current directory")
    print("=" * 50)


if __name__ == "__main__":
    main()