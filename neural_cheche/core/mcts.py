"""
Monte Carlo Tree Search implementation
"""

import numpy as np
import torch
from ..utils.gpu_utils import clear_gpu_memory


class MCTSNode:
    """Node in the MCTS tree"""

    def __init__(self, game, board, parent=None, prior=1.0):
        self.game = game
        self.board = board
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0
        self.prior = prior

    def is_leaf(self):
        """Check if this is a leaf node"""
        return not self.children

    @property
    def Q(self):
        """Q-value is the average value of this node"""
        return self.value

    def select(self, c_puct=1.0):
        """Select best child using UCB formula"""
        return max(
            self.children.items(),
            key=lambda item: item[1].Q
            + c_puct * item[1].prior * np.sqrt(self.visits) / (1 + item[1].visits),
        )

    def expand(self, policy, legal_moves):
        """Expand node with children for all legal moves"""
        for move, prob in zip(legal_moves, policy):
            if move not in self.children:
                board_copy = self.game.copy_board(self.board)
                self.game.make_move(board_copy, move)
                self.children[move] = MCTSNode(self.game, board_copy, self, prob)

    def backpropagate(self, value):
        """Backpropagate value up the tree"""
        self.visits += 1
        self.value += (value - self.value) / self.visits
        if self.parent:
            self.parent.backpropagate(-value)


class MCTS:
    """Monte Carlo Tree Search for game playing"""

    def __init__(self, game, net, num_simulations=25):
        self.game = game
        self.net = net
        self.num_simulations = num_simulations
        self.device = net.get_device()

    def search(self, board):
        """Run MCTS search and return policy"""
        print(f"[MCTS] Starting search with {self.num_simulations} simulations")

        root = MCTSNode(self.game, board)

        # Get legal moves
        legal_moves = self.game.get_legal_moves(board)
        if not legal_moves:
            print("[MCTS] No legal moves available")
            return {}

        print(f"[MCTS] Found {len(legal_moves)} legal moves")

        # Initial policy evaluation
        try:
            policy, _ = self._evaluate_position(board)

            # Add Dirichlet noise for exploration
            alpha = 0.3
            noise = np.random.dirichlet([alpha] * len(legal_moves))
            epsilon = 0.25
            noisy_policy = (1 - epsilon) * policy[: len(legal_moves)] + epsilon * noise

            root.expand(noisy_policy, legal_moves)
            print(f"[MCTS] Root expanded with {len(root.children)} children")

        except Exception as e:
            print(f"[MCTS] Error in initial evaluation: {e}")
            # Fallback to uniform policy
            uniform_policy = np.ones(len(legal_moves)) / len(legal_moves)
            root.expand(uniform_policy, legal_moves)

        # Run simulations
        for sim_idx in range(self.num_simulations):
            try:
                if sim_idx % 5 == 0:
                    print(f"[MCTS] Simulation {sim_idx}/{self.num_simulations}")
                    self._process_events()  # Keep GUI responsive

                self._simulate(root)

            except Exception as e:
                print(f"[MCTS] Simulation {sim_idx} failed: {e}")
                continue

        # Clear GPU memory after search
        clear_gpu_memory()

        # Return visit counts as policy
        if not root.children:
            print("[MCTS] Warning: No children in root node")
            return {}

        total_visits = sum(child.visits for child in root.children.values())
        if total_visits == 0:
            print("[MCTS] Warning: No visits recorded")
            return {move: 1.0 / len(root.children) for move in root.children.keys()}

        result = {
            move: child.visits / total_visits for move, child in root.children.items()
        }
        print(f"[MCTS] Search complete. Returning policy with {len(result)} moves")
        return result

    def _simulate(self, root):
        """Run a single MCTS simulation"""
        node = root
        sim_board = self.game.copy_board(root.board)

        # Selection phase
        while not node.is_leaf():
            move, node = node.select()
            self.game.make_move(sim_board, move)

        # Expansion and evaluation phase
        if not self.game.is_game_over(sim_board):
            try:
                policy, value = self._evaluate_position(sim_board)
                legal_moves = self.game.get_legal_moves(sim_board)
                if legal_moves:
                    node.expand(policy[: len(legal_moves)], legal_moves)
                else:
                    value = self.game.get_reward(sim_board)
            except Exception:
                value = self.game.get_reward(sim_board)
        else:
            value = self.game.get_reward(sim_board)

        # Backpropagation phase
        node.backpropagate(value)

    def _evaluate_position(self, board):
        """Evaluate position using neural network"""
        state_tensor = self.game.board_to_tensor(
            board, [], device=torch.device("cpu")
        ).unsqueeze(0)

        # Move to device for inference
        if self.device.type != "cpu":
            state_tensor = state_tensor.to(self.device)

        with torch.no_grad():
            policy, value = self.net(state_tensor, self.game.name)
            policy = policy.detach().cpu().numpy().flatten()
            value = value.detach().cpu().item()

        return policy, value

    def _process_events(self):
        """Process pygame events to keep GUI responsive"""
        try:
            import pygame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[MCTS] User requested quit during search")
                    return False
        except ImportError:
            pass  # Pygame not available
        return True


def run_mcts(board, net, game_type, num_simulations=25):
    """Convenience function to run MCTS (backward compatibility)"""
    # Import game classes
    from ..games import ChessGame, CheckersGame

    # Create appropriate game instance
    if game_type == "chess":
        game = ChessGame()
    elif game_type == "checkers":
        game = CheckersGame()
    else:
        raise ValueError(f"Unsupported game type: {game_type}")

    # Run MCTS
    mcts = MCTS(game, net, num_simulations)
    return mcts.search(board)
