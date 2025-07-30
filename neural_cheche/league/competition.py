"""
Competition and match management
"""

import json
import random
import time
import uuid
from datetime import datetime
from ..games import ChessGame, CheckersGame
from ..core import MCTS
from ..utils import clear_gpu_memory
from ..validation import MoveValidator
from ..history import MoveLogger, MoveData, GameInfo, GameResult, ScoreTracker


class Match:
    """Represents a single game match between two agents"""
    
    def __init__(self, agent1, agent2, game_type, visualize=False, enable_validation=True, 
                 generation=0, move_logger=None, score_tracker=None):
        self.agent1 = agent1
        self.agent2 = agent2
        self.game_type = game_type
        self.visualize = visualize
        self.enable_validation = enable_validation
        self.generation = generation
        
        # History tracking
        self.move_logger = move_logger
        self.score_tracker = score_tracker
        self.game_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # Create game instance
        if game_type == "chess":
            self.game = ChessGame()
        elif game_type == "checkers":
            self.game = CheckersGame()
        else:
            raise ValueError(f"Unsupported game type: {game_type}")
        
        # Create move validator
        self.validator = MoveValidator(game_type) if enable_validation else None
        
        # Match state
        self.board = None
        self.history = []
        self.experiences = []
        self.move_count = 0
        self.max_moves = 200
        self.winner = None
        self.final_reward = 0
        self.validation_violations = []
        self.captured_pieces = {"white": [], "black": []}
    
    def play(self, replay_buffer=None, renderer=None, visualization_manager=None):
        """Play the match and return experiences and result"""
        print(f"[Match] Starting {self.game_type} match: {self.agent1.name} vs {self.agent2.name}")
        
        # Initialize game logging
        if self.move_logger:
            game_info = GameInfo(
                game_id=self.game_id,
                generation=self.generation,
                agent1_name=self.agent1.name,
                agent2_name=self.agent2.name,
                game_type=self.game_type,
                start_time=self.start_time,
                max_moves=self.max_moves,
                visualization_enabled=self.visualize,
                validation_enabled=self.enable_validation
            )
            self.move_logger.start_game_log(game_info)
        
        # Initialize the board
        self.board = self.game.create_board()
        self.history = []
        self.experiences = []
        self.move_count = 0
        
        try:
            while not self.game.is_game_over(self.board) and self.move_count < self.max_moves:
                # Determine current player and agent
                current_player = self.game.get_current_player(self.board)
                current_agent = self.agent1 if current_player == 1 else self.agent2
                
                if self.visualize and visualization_manager:
                    self._update_visualization(visualization_manager, renderer, current_agent)
                
                # Get move from agent with validation retry logic
                move = self._get_validated_move(current_agent)
                if move is None:
                    print("[Match] No valid move found, ending game")
                    break
                
                # Store board state before move for logging
                board_before = self.game.copy_board(self.board)
                
                # Record experience
                self._record_experience(current_agent, move)
                
                # Make move (validation is handled in _get_validated_move)
                move_start_time = time.time()
                self.game.make_move(self.board, move)
                move_end_time = time.time()
                
                self.history.append(self.game.copy_board(self.board))
                self.move_count += 1
                
                # Log the move if move logger is available
                if self.move_logger:
                    self._log_move(current_agent, move, board_before, self.board, 
                                 move_end_time - move_start_time)
                
                # Update score tracker
                if self.score_tracker:
                    self._update_live_scores()
                
                print(f"[Match] Move {self.move_count}: {current_agent.name} played {move}")
                
                if self.visualize and visualization_manager:
                    self._show_move_result(visualization_manager, renderer, move)
            
            # Determine winner and assign rewards
            self._finalize_match()
            
        except Exception as e:
            print(f"[Match] Error during match: {e}")
            self.final_reward = 0
        
        finally:
            clear_gpu_memory()
        
        # Add experiences to replay buffer
        if replay_buffer and self.experiences:
            replay_buffer.add(self.experiences)
        
        return self.experiences, self.final_reward
    
    def _get_validated_move(self, agent, max_retries=3):
        """Get a validated move from the specified agent"""
        for attempt in range(max_retries):
            try:
                # Get move from agent
                move = self._get_agent_move(agent)
                if move is None:
                    return None
                
                # Validate move if validation is enabled
                if self.validator:
                    board_before = self.game.copy_board(self.board)
                    
                    # Test the move on a copy
                    test_board = self.game.copy_board(self.board)
                    try:
                        self.game.make_move(test_board, move)
                        
                        # Validate the move
                        validation_result = self.validator.validate_move(
                            board_before, test_board, move,
                            agent_name=agent.name,
                            generation=self.generation,
                            move_number=self.move_count + 1
                        )
                        
                        if validation_result.is_valid:
                            return move
                        else:
                            # Log violation and try again
                            self.validation_violations.append(validation_result)
                            print(f"⚠️ Invalid move detected from {agent.name}: {validation_result.get_violation_summary()}")
                            
                            if attempt == max_retries - 1:
                                print(f"❌ Max retries reached for {agent.name}, using fallback move")
                                return self._get_fallback_move()
                    
                    except Exception as move_error:
                        print(f"⚠️ Move execution failed: {move_error}")
                        if attempt == max_retries - 1:
                            return self._get_fallback_move()
                else:
                    # No validation, return move directly
                    return move
                    
            except Exception as e:
                print(f"[Match] Error getting validated move from {agent.name} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return self._get_fallback_move()
        
        return None
    
    def _get_agent_move(self, agent):
        """Get a move from the specified agent"""
        try:
            # Use MCTS to get policy
            mcts = MCTS(self.game, agent.net, num_simulations=25)
            policy = mcts.search(self.board)
            
            if not policy:
                # Fallback to random legal move
                legal_moves = self.game.get_legal_moves(self.board)
                return random.choice(legal_moves) if legal_moves else None
            
            # Select move based on policy
            moves = list(policy.keys())
            probs = list(policy.values())
            
            # Add some exploration
            if random.random() < 0.1:  # 10% exploration
                return random.choice(moves)
            else:
                return random.choices(moves, weights=probs, k=1)[0]
        
        except Exception as e:
            print(f"[Match] Error getting move from {agent.name}: {e}")
            # Fallback to random move
            legal_moves = self.game.get_legal_moves(self.board)
            return random.choice(legal_moves) if legal_moves else None
    
    def _get_fallback_move(self):
        """Get a safe fallback move when validation fails"""
        try:
            legal_moves = self.game.get_legal_moves(self.board)
            if legal_moves:
                # Try to find a safe move (not just random)
                for move in legal_moves:
                    try:
                        test_board = self.game.copy_board(self.board)
                        self.game.make_move(test_board, move)
                        # If we can make the move without error, use it
                        return move
                    except Exception:
                        continue
                
                # If no safe move found, use first legal move
                return legal_moves[0]
            
            return None
            
        except Exception as e:
            print(f"[Match] Error getting fallback move: {e}")
            return None
    
    def _record_experience(self, agent, move):
        """Record experience for training"""
        try:
            # Create state tensor
            state_tensor = self.game.board_to_tensor(self.board, self.history[-8:])
            
            # Create simple policy (this would be more sophisticated in practice)
            policy = {str(move): 1.0}
            
            # Experience format: [state, policy, reward, agent_name]
            experience = [state_tensor, policy, None, agent.name]
            self.experiences.append(experience)
            
        except Exception as e:
            print(f"[Match] Error recording experience: {e}")
    
    def _finalize_match(self):
        """Finalize the match and assign rewards"""
        self.winner = self.game.get_winner(self.board)
        self.final_reward = self.game.get_reward(self.board)
        
        # Assign rewards to experiences
        for exp in self.experiences:
            agent_name = exp[3]
            if agent_name == self.agent1.name:
                exp[2] = self.final_reward
            else:
                exp[2] = -self.final_reward
        
        # Record results for agents
        agent1_won = self.final_reward > 0
        agent2_won = self.final_reward < 0
        
        self.agent1.record_game_result(self.game_type, agent1_won, self.final_reward)
        self.agent2.record_game_result(self.game_type, agent2_won, -self.final_reward)
        
        # Finalize game logging
        self._finalize_game_logging()
        
        print(f"[Match] Game finished. Winner: {self._get_winner_name()}, Reward: {self.final_reward}")
    
    def _get_winner_name(self):
        """Get the name of the winning agent"""
        if self.final_reward > 0:
            return self.agent1.name
        elif self.final_reward < 0:
            return self.agent2.name
        else:
            return "Draw"
    
    def _update_visualization(self, vis_manager, renderer, current_agent):
        """Update visualization during the match"""
        if not vis_manager or not renderer:
            return
        
        vis_manager.clear_screen()
        
        # Draw the board
        offset_x = vis_manager.chess_offset_x if self.game_type == "chess" else vis_manager.checkers_offset_x
        title = f"{self.game_type.title()} - {current_agent.name} thinking..."
        
        renderer.draw_board(
            vis_manager.screen, self.board, 
            offset_x, vis_manager.board_offset_y, 
            title
        )
        
        # Show thinking indicator
        vis_manager.display_thinking_indicator(
            self.game_type, current_agent.name, self.move_count
        )
        
        vis_manager.refresh_display()
        vis_manager.process_events()
    
    def _show_move_result(self, vis_manager, renderer, move):
        """Show the result of a move"""
        if not vis_manager or not renderer:
            return
        
        vis_manager.clear_screen()
        
        # Draw updated board
        offset_x = vis_manager.chess_offset_x if self.game_type == "chess" else vis_manager.checkers_offset_x
        title = f"{self.game_type.title()} - Move {self.move_count}"
        
        renderer.draw_board(
            vis_manager.screen, self.board,
            offset_x, vis_manager.board_offset_y,
            title, last_move=move
        )
        
        # Show move statistics
        vis_manager.display_move_statistics(self.game_type, self.move_count, self.max_moves)
        
        vis_manager.refresh_display()
        
        # Brief pause to show the move
        vis_manager.wait_with_events(0.1)
    
    def _log_move(self, agent, move, board_before, board_after, thinking_time):
        """Log a move to the move logger"""
        try:
            if not self.move_logger:
                return
            
            # Get captured pieces
            captured_pieces = self.game.get_captured_pieces_from_move(board_before, board_after, move)
            
            # Create move data
            move_data = MoveData(
                game_id=self.game_id,
                generation=self.generation,
                agent_name=agent.name,
                game_type=self.game_type,
                move_number=self.move_count,
                move=str(move),
                board_state_before=self.game.get_board_string(board_before),
                board_state_after=self.game.get_board_string(board_after),
                evaluation_score=0.0,  # Could be enhanced with actual evaluation
                policy_distribution={},  # Could be enhanced with actual policy
                thinking_time=thinking_time,
                captured_pieces=captured_pieces,
                timestamp=datetime.now(),
                is_valid=True  # Since we validated it already
            )
            
            # Log the move
            self.move_logger.log_move(move_data)
            
        except Exception as e:
            print(f"⚠️ Error logging move: {e}")
    
    def _update_live_scores(self):
        """Update live scores in the score tracker"""
        try:
            if not self.score_tracker:
                return
            
            # Calculate current scores (simplified)
            # In a real implementation, this would be more sophisticated
            agent1_score = 0.5 + (self.final_reward * 0.5) if hasattr(self, 'final_reward') else 0.5
            agent2_score = 0.5 - (self.final_reward * 0.5) if hasattr(self, 'final_reward') else 0.5
            
            self.score_tracker.update_current_scores(
                agent1_score, agent2_score, 
                self.agent1.name, self.agent2.name
            )
            
        except Exception as e:
            print(f"⚠️ Error updating live scores: {e}")
    
    def _finalize_game_logging(self):
        """Finalize logging when game ends"""
        try:
            # End game logging
            if self.move_logger:
                end_time = datetime.now()
                game_duration = (end_time - self.start_time).total_seconds()
                
                # Create game result
                game_result = GameResult(
                    game_id=self.game_id,
                    winner=self._get_winner_name(),
                    final_score={
                        self.agent1.name: 1.0 if self.final_reward > 0 else (0.0 if self.final_reward < 0 else 0.5),
                        self.agent2.name: 1.0 if self.final_reward < 0 else (0.0 if self.final_reward > 0 else 0.5)
                    },
                    total_moves=self.move_count,
                    game_duration=game_duration,
                    termination_reason="Normal completion" if self.move_count < self.max_moves else "Max moves reached",
                    captured_pieces=self.captured_pieces,
                    final_board_state=self.game.get_board_string(self.board),
                    end_time=end_time
                )
                
                # End the game log
                self.move_logger.end_game_log(self.game_id, game_result)
                
                # Create backup
                self.move_logger.create_backup(self.game_id)
            
            # Record final result in score tracker
            if self.score_tracker:
                game_result = GameResult(
                    game_id=self.game_id,
                    winner=self._get_winner_name(),
                    final_score={
                        self.agent1.name: 1.0 if self.final_reward > 0 else (0.0 if self.final_reward < 0 else 0.5),
                        self.agent2.name: 1.0 if self.final_reward < 0 else (0.0 if self.final_reward > 0 else 0.5)
                    },
                    total_moves=self.move_count,
                    game_duration=(datetime.now() - self.start_time).total_seconds(),
                    termination_reason="Normal completion" if self.move_count < self.max_moves else "Max moves reached",
                    captured_pieces=self.captured_pieces,
                    final_board_state=self.game.get_board_string(self.board),
                    end_time=datetime.now()
                )
                
                self.score_tracker.record_game_result(game_result)
            
        except Exception as e:
            print(f"⚠️ Error finalizing game logging: {e}")


class Competition:
    """Manages competitions between agents"""
    
    def __init__(self, visualization_manager=None, enable_validation=True, enable_history=True):
        self.visualization_manager = visualization_manager
        self.enable_validation = enable_validation
        self.enable_history = enable_history
        self.match_history = []
        self.validation_statistics = {
            'total_violations': 0,
            'violations_by_agent': {},
            'violations_by_game_type': {}
        }
        
        # Initialize history tracking components
        self.move_logger = None
        self.score_tracker = None
        
        if self.enable_history:
            try:
                self.move_logger = MoveLogger("move_history")
                self.score_tracker = ScoreTracker("score_history.json")
                print("📝 History tracking initialized for Competition")
            except Exception as e:
                print(f"⚠️ Failed to initialize history tracking: {e}")
                self.enable_history = False
    
    def play_match(self, agent1, agent2, game_type, visualize=False, replay_buffer=None, generation=0):
        """Play a single match between two agents"""
        # Get appropriate renderer
        renderer = None
        if visualize and self.visualization_manager:
            if game_type == "chess":
                from ..games.chess import ChessRenderer
                renderer = ChessRenderer()
            elif game_type == "checkers":
                from ..games.checkers import CheckersRenderer
                renderer = CheckersRenderer()
        
        # Create and play match
        match = Match(agent1, agent2, game_type, visualize, self.enable_validation, generation,
                     self.move_logger if self.enable_history else None,
                     self.score_tracker if self.enable_history else None)
        experiences, reward = match.play(replay_buffer, renderer, self.visualization_manager)
        
        # Update validation statistics
        if match.validation_violations:
            self._update_validation_statistics(match.validation_violations, agent1.name, agent2.name, game_type)
        
        # Record match in history
        self.match_history.append({
            'agent1': agent1.name,
            'agent2': agent2.name,
            'game_type': game_type,
            'winner': match._get_winner_name(),
            'reward': reward,
            'move_count': match.move_count,
            'validation_violations': len(match.validation_violations),
            'timestamp': time.time()
        })
        
        return experiences, reward
    
    def play_tournament(self, agents, game_types, rounds_per_matchup=1, visualize=False, replay_buffer=None):
        """Play a round-robin tournament between agents"""
        results = {}
        
        for game_type in game_types:
            results[game_type] = {}
            
            # Play all matchups
            for i, agent1 in enumerate(agents):
                for j, agent2 in enumerate(agents):
                    if i != j:  # Don't play against self
                        matchup_key = f"{agent1.name}_vs_{agent2.name}"
                        results[game_type][matchup_key] = []
                        
                        for round_num in range(rounds_per_matchup):
                            print(f"[Tournament] {game_type} Round {round_num + 1}: {agent1.name} vs {agent2.name}")
                            
                            experiences, reward = self.play_match(
                                agent1, agent2, game_type, visualize, replay_buffer
                            )
                            
                            results[game_type][matchup_key].append({
                                'reward': reward,
                                'winner': agent1.name if reward > 0 else (agent2.name if reward < 0 else "Draw"),
                                'experiences_count': len(experiences)
                            })
        
        return results
    
    def evaluate_agents(self, challenger, champion, game_types, num_games=10):
        """Evaluate challenger against champion"""
        total_wins = 0
        total_games = 0
        
        for game_type in game_types:
            wins = 0
            for game_num in range(num_games):
                print(f"[Evaluation] {game_type} Game {game_num + 1}/{num_games}")
                
                experiences, reward = self.play_match(
                    challenger, champion, game_type, visualize=False
                )
                
                if reward > 0:  # Challenger won
                    wins += 1
                
                total_games += 1
            
            total_wins += wins
            win_rate = wins / num_games
            print(f"[Evaluation] {game_type} win rate: {win_rate:.2%}")
        
        overall_win_rate = total_wins / total_games
        print(f"[Evaluation] Overall win rate: {overall_win_rate:.2%}")
        
        return overall_win_rate
    
    def get_match_statistics(self):
        """Get statistics about played matches"""
        if not self.match_history:
            return {}
        
        stats = {
            'total_matches': len(self.match_history),
            'game_type_counts': {},
            'agent_performance': {},
            'average_game_length': 0
        }
        
        # Count by game type
        for match in self.match_history:
            game_type = match['game_type']
            stats['game_type_counts'][game_type] = stats['game_type_counts'].get(game_type, 0) + 1
        
        # Agent performance
        for match in self.match_history:
            for agent_key in ['agent1', 'agent2']:
                agent_name = match[agent_key]
                if agent_name not in stats['agent_performance']:
                    stats['agent_performance'][agent_name] = {'wins': 0, 'games': 0}
                
                stats['agent_performance'][agent_name]['games'] += 1
                if match['winner'] == agent_name:
                    stats['agent_performance'][agent_name]['wins'] += 1
        
        # Average game length
        total_moves = sum(match['move_count'] for match in self.match_history)
        stats['average_game_length'] = total_moves / len(self.match_history)
        
        return stats
    
    def _update_validation_statistics(self, violations, agent1_name, agent2_name, game_type):
        """Update validation statistics with new violations"""
        for violation in violations:
            self.validation_statistics['total_violations'] += 1
            
            # Count by game type
            if game_type not in self.validation_statistics['violations_by_game_type']:
                self.validation_statistics['violations_by_game_type'][game_type] = 0
            self.validation_statistics['violations_by_game_type'][game_type] += 1
            
            # Count by agent (violations contain agent names)
            for agent_name in [agent1_name, agent2_name]:
                if agent_name not in self.validation_statistics['violations_by_agent']:
                    self.validation_statistics['violations_by_agent'][agent_name] = 0
                # Note: We'd need to check the violation details to know which agent caused it
                # For now, we'll increment both agents' counts
                self.validation_statistics['violations_by_agent'][agent_name] += 0.5
    
    def get_validation_report(self):
        """Get a comprehensive validation report"""
        if not self.enable_validation:
            return {"validation_enabled": False}
        
        report = {
            "validation_enabled": True,
            "total_violations": self.validation_statistics['total_violations'],
            "violations_by_game_type": self.validation_statistics['violations_by_game_type'].copy(),
            "violations_by_agent": self.validation_statistics['violations_by_agent'].copy(),
            "violation_rate": 0.0
        }
        
        # Calculate violation rate
        total_matches = len(self.match_history)
        if total_matches > 0:
            report["violation_rate"] = self.validation_statistics['total_violations'] / total_matches
        
        return report
    
    def get_history_statistics(self):
        """Get comprehensive history tracking statistics"""
        if not self.enable_history:
            return {"history_enabled": False}
        
        stats = {"history_enabled": True}
        
        # Move logger statistics
        if self.move_logger:
            stats["move_logging"] = self.move_logger.get_statistics()
        
        # Score tracker statistics
        if self.score_tracker:
            stats["score_tracking"] = {
                "current_scores": self.score_tracker.get_live_scores(),
                "total_games_tracked": self.score_tracker.performance_metrics.get('total_games_tracked', 0),
                "leaderboard": self.score_tracker.get_leaderboard(limit=5)
            }
        
        return stats
    
    def export_history_report(self, output_file: str = None):
        """Export comprehensive history report"""
        if not self.enable_history:
            print("⚠️ History tracking not enabled")
            return ""
        
        try:
            # Generate timestamp if no output file specified
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"competition_history_report_{timestamp}.json"
            
            # Collect all history data
            report = {
                "report_info": {
                    "generated_at": datetime.now().isoformat(),
                    "competition_matches": len(self.match_history),
                    "validation_enabled": self.enable_validation,
                    "history_enabled": self.enable_history
                },
                "match_history": self.match_history,
                "validation_statistics": self.validation_statistics,
                "history_statistics": self.get_history_statistics()
            }
            
            # Add detailed reports from history components
            if self.score_tracker:
                report["performance_report"] = self.score_tracker.export_performance_report()
            
            # Save report
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📋 Competition history report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"⚠️ Error exporting history report: {e}")
            return ""
    
    def cleanup_history(self, days_to_keep: int = 30):
        """Clean up old history files"""
        if not self.enable_history:
            return
        
        try:
            if self.move_logger:
                self.move_logger.cleanup_old_files(days_to_keep)
            
            print(f"🧹 History cleanup completed (kept {days_to_keep} days)")
            
        except Exception as e:
            print(f"⚠️ Error during history cleanup: {e}")
    
    def get_agent_performance_summary(self, agent_name: str):
        """Get detailed performance summary for a specific agent"""
        if not self.enable_history or not self.score_tracker:
            return {"error": "History tracking not available"}
        
        return self.score_tracker.get_agent_summary(agent_name)
    
    def get_recent_games(self, limit: int = 10):
        """Get recent game history"""
        if not self.enable_history or not self.move_logger:
            return []
        
        return self.move_logger.get_recent_games(limit)