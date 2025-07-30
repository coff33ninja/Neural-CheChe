# Neural CheChe: Modular AI Training System

## 🎯 Overview

Neural CheChe is a professional, modular AI training system that teaches neural networks to play both Chess and Checkers through self-play, strategic discussions, and competitive evolution. The system uses a Champion-Challenger architecture where multiple AI agents learn from each other through structured competition and knowledge sharing.

## 🏗️ Architecture

### Modular Structure
```
neural_cheche/
├── games/                    # Game implementations
│   ├── base_game.py         # Abstract game interface
│   ├── chess/               # Chess-specific components
│   │   ├── chess_game.py    # Chess game logic
│   │   └── chess_renderer.py # Chess visualization
│   └── checkers/            # Checkers-specific components
│       ├── checkers_game.py # Checkers game logic
│       └── checkers_renderer.py # Checkers visualization
├── core/                    # Core AI components
│   ├── neural_net.py       # Neural network architecture
│   ├── mcts.py             # Monte Carlo Tree Search
│   ├── replay_buffer.py    # Experience replay
│   └── training.py         # Training algorithms
├── league/                  # League management
│   ├── league_manager.py   # Main orchestration
│   ├── agents.py           # AI agent definitions
│   └── competition.py      # Match and tournament logic
├── utils/                   # Utilities
│   ├── gpu_utils.py        # GPU management
│   ├── game_utils.py       # Game utilities
│   └── visualization.py    # GUI management
├── config/                  # Configuration
│   └── settings.py         # Configuration management
└── __init__.py             # Package interface
```

### Core Components

#### Neural Network (`neural_net.py`)
- **Unified GameNet**: Single neural network that plays both chess and checkers
- **Shared Backbone**: Common feature extraction layers
- **Game-Specific Heads**: Separate policy and value heads for each game
- **Board Representation**: Converts game states to tensor format

#### Monte Carlo Tree Search (`mcts.py`)
- **Strategic Planning**: AI uses MCTS to evaluate potential moves
- **Neural-Guided Search**: Combines neural network evaluation with tree search
- **Dirichlet Noise**: Adds exploration to prevent overfitting
- **Optimized Performance**: Configurable simulations per move

#### League Management (`league_manager.py`)
- **Training Orchestration**: Manages the entire learning process
- **Generational Evolution**: Structured improvement cycles
- **Visual Interface**: Real-time pygame display of games
- **Progress Tracking**: Comprehensive statistics and model saving

## 🤖 Agent System

### Champion Agent
- **Role**: Current best performer
- **Features**: Tracks promotion history and defense record
- **Behavior**: Leads training and defends against challengers

### Training Agents (Alpha & Beta)
- **Alpha**: Specializes in opening strategies
- **Beta**: Focuses on endgame techniques
- **Features**: Specialized learning focuses and training metrics
- **Behavior**: Learn from champion and compete for promotion

### Wildcard Agent
- **Role**: Fresh baseline for absolute skill measurement
- **Features**: Resets to random state, tracks improvement trends
- **Behavior**: Provides consistent baseline for progress evaluation

## 🎮 Training Process

### Phase 1: Game Generation
Each generation consists of structured matches:
- Champion self-play for training data
- Alpha vs Beta competitive learning
- Cross-game knowledge transfer (chess ↔ checkers)

### Phase 2: AI Strategy Discussion
- Neural network training on collected experiences
- Specialized learning for each agent type
- Shared knowledge integration

### Phase 3: Challenger System (Every 5 Generations)
- Best training agent challenges champion
- Promotion if win rate > 55%
- Knowledge transfer to all agents

### Phase 4: Wildcard Challenge (Every 3 Generations)
- Champion tested against fresh AI
- Absolute skill measurement
- Progress trend analysis

## 🚀 Getting Started

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Additional GPU support (optional)
pip install torch-directml  # For Windows GPU acceleration
```

### Quick Start
```bash
# Show system information
python main.py --info

# Run training (5 generations for testing)
python main.py --generations 5

# Use training-optimized settings
python main.py --config training --generations 50

# Run without visualization (faster)
python main.py --no-viz --fast
```

### Advanced Usage
```bash
# Resume from checkpoint
python main.py --load-checkpoint 25

# Use custom configuration file
python main.py --config-file my_config.json

# Save current configuration
python main.py --save-config my_settings.json
```

## ⚙️ Configuration

### Preset Configurations

#### Training Configuration
Optimized for learning performance:
```bash
python main.py --config training
```
- Higher MCTS simulations (50)
- More training steps per generation (100)
- Frequent challenger evaluations

#### Fast Configuration
Optimized for speed:
```bash
python main.py --config fast
```
- Reduced MCTS simulations (10)
- Smaller batch sizes
- Faster move delays

#### Visualization Configuration
Optimized for watching games:
```bash
python main.py --config visualization
```
- Larger window and pieces
- Slower move delays for better viewing
- Enhanced visual feedback

### Custom Configuration
Create your own configuration file:
```json
{
  "learning_rate": 0.001,
  "batch_size": 64,
  "mcts_simulations": 25,
  "enable_visualization": true,
  "challenger_threshold": 0.55
}
```

## 🔧 Technical Features

### GPU Optimization
- **Universal GPU Support**: CUDA, DirectML, MPS, CPU fallback
- **Memory Management**: Automatic GPU memory cleanup
- **Stable Performance**: Handles GPU device suspension gracefully
- **Cross-Platform**: Works on Windows, Mac, Linux

### Responsive GUI
- **Real-Time Visualization**: Watch AIs play live games
- **Move-by-Move Display**: See thinking process and move selection
- **Progress Indicators**: Generation tracking, win statistics
- **Interactive Controls**: Pygame-based interface with event handling

### Data Management
- **Replay Buffer**: Stores game experiences for learning
- **Model Persistence**: Automatic saving of neural networks
- **Progress Tracking**: JSON logs of training statistics
- **Experience Sharing**: AIs learn from each other's games

## 🎯 Adding New Games

The modular architecture makes it easy to add new games:

1. **Create Game Class**:
```python
class MyGame(BaseGame):
    def create_board(self):
        # Initialize game board
        pass
    
    def get_legal_moves(self, board):
        # Return legal moves
        pass
    
    # Implement other required methods...
```

2. **Create Renderer**:
```python
class MyGameRenderer:
    def draw_board(self, screen, board, x, y, title):
        # Draw the game board
        pass
```

3. **Register Game**:
```python
# Add to games/__init__.py
from .mygame import MyGame, MyGameRenderer
```

## 📊 Performance Monitoring

### Real-time Statistics
- Generation progress and phase tracking
- Agent win rates and performance metrics
- Buffer utilization and training loss
- GPU memory usage and optimization

### Saved Data
- Model checkpoints every 10 generations
- Training statistics in JSON format
- Match history and competition results
- Agent performance trends

### 🛠️ Development Mode
```bash
# Enable detailed logging
python main.py --config training --generations 5

# Test specific components
python -c "from neural_cheche.games import ChessGame; game = ChessGame(); print('Chess OK')"
python -c "from neural_cheche.utils import get_gpu_info; print(get_gpu_info())"
```

## 🔮 Future Extensions

The modular architecture enables easy extensions:

### New Games
- **Go**: Complex board game with different rules
- **Othello/Reversi**: Disc-flipping strategy game
- **Connect Four**: Vertical strategy game

### Advanced Features
- **Multi-GPU Training**: Distributed training across multiple GPUs
- **Human Interaction**: Play against trained AIs
- **Tournament Mode**: AI vs AI competitions
- **Opening Books**: Specialized knowledge databases

### Research Applications
- **Transfer Learning**: Knowledge transfer between games
- **Meta-Learning**: Learning to learn new games quickly
- **Curriculum Learning**: Progressive difficulty training

## 📈 Expected Outcomes

As training progresses, you should observe:
1. **Improving Wildcard Scores**: Better performance vs random opponents
2. **Strategic Gameplay**: More sophisticated move selection
3. **Cross-Game Learning**: Chess skills improving checkers play
4. **Stable Convergence**: Consistent high-level performance

## 🤝 Contributing

The modular structure makes contributions easier:

1. **Game Implementations**: Add new games following the `BaseGame` interface
2. **Training Algorithms**: Enhance the training system in `core/training.py`
3. **Visualization**: Improve GUI components in `utils/visualization.py`
4. **Configuration**: Add new presets in `config/settings.py`

## 🏆 Key Innovations

### Human-Like Learning
- **Strategic Discussions**: AIs analyze games like human players
- **Specialized Roles**: Different AIs focus on different aspects
- **Knowledge Sharing**: Collaborative improvement process

### Dual-Game Training
- **Cross-Pollination**: Chess knowledge helps checkers and vice versa
- **Strategic Diversity**: Different games teach different patterns
- **Unified Intelligence**: Single network masters both games

### Evolutionary Competition
- **Champion System**: Best AI leads the training
- **Challenger Battles**: Regular skill tests and promotions
- **Wildcard Audits**: Absolute progress measurement

## 📄 Requirements

See `requirements.txt` for complete dependency list. Key requirements:
- Python 3.8+
- PyTorch (with optional GPU support)
- python-chess
- draughts
- pygame
- numpy

## 🔒 Safety

All original files are safely preserved in the `backup/` directory for reference and rollback if needed.

---

**Neural CheChe**: Where modular design meets artificial intelligence mastery through competitive evolution and collaborative learning.