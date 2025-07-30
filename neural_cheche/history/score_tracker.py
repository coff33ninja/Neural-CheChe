"""
Score Tracker - Real-time score tracking and performance analysis
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict, deque

from .data_models import GameResult, HistoryEncoder


class ScoreTracker:
    """Tracks scores and performance metrics in real-time"""
    
    def __init__(self, history_file: str = "score_history.json"):
        self.history_file = Path(history_file)
        
        # Current state
        self.current_scores: Dict[str, float] = {}
        self.live_games: Dict[str, Dict[str, Any]] = {}
        
        # Historical data
        self.game_results: List[GameResult] = []
        self.agent_performance: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total_score': 0.0,
            'average_score': 0.0,
            'win_rate': 0.0,
            'recent_performance': deque(maxlen=20)  # Last 20 games
        })
        
        # Performance metrics
        self.performance_metrics: Dict[str, Any] = {
            'total_games_tracked': 0,
            'total_moves_tracked': 0,
            'average_game_length': 0.0,
            'most_active_agent': '',
            'best_performing_agent': '',
            'tracking_start_time': datetime.now()
        }
        
        # Load existing data
        self._load_history()
        
        print(f"📊 ScoreTracker initialized with {len(self.game_results)} historical games")
    
    def update_current_scores(self, player1_score: float, player2_score: float, 
                            player1_name: str = "Player1", player2_name: str = "Player2") -> None:
        """
        Update current live scores
        
        Args:
            player1_score: Current score for player 1
            player2_score: Current score for player 2
            player1_name: Name of player 1
            player2_name: Name of player 2
        """
        try:
            self.current_scores[player1_name] = player1_score
            self.current_scores[player2_name] = player2_score
            
            # Update live game tracking if needed
            # This could be expanded to track multiple simultaneous games
            
        except Exception as e:
            print(f"⚠️ Error updating current scores: {e}")
    
    def record_game_result(self, result: GameResult) -> None:
        """
        Record a completed game result
        
        Args:
            result: Complete game result data
        """
        try:
            # Add to results history
            self.game_results.append(result)
            
            # Update agent performance
            self._update_agent_performance(result)
            
            # Update overall metrics
            self._update_performance_metrics(result)
            
            # Save to disk periodically
            if len(self.game_results) % 10 == 0:  # Save every 10 games
                self._save_history()
            
            print(f"📊 Recorded game result: {result.winner} won in {result.total_moves} moves")
            
        except Exception as e:
            print(f"⚠️ Error recording game result: {e}")
    
    def get_historical_trends(self, agent_name: str, timeframe: str = "all") -> List[Dict[str, Any]]:
        """
        Get historical performance trends for an agent
        
        Args:
            agent_name: Name of the agent
            timeframe: Time period ("all", "recent", "daily", "weekly")
            
        Returns:
            List of performance data points
        """
        try:
            # Filter games for this agent
            agent_games = [
                result for result in self.game_results
                if agent_name in [result.winner, result.final_score.get('player1_name'), result.final_score.get('player2_name')]
            ]
            
            # Apply timeframe filter
            if timeframe == "recent":
                agent_games = agent_games[-20:]  # Last 20 games
            elif timeframe == "daily":
                cutoff = datetime.now() - timedelta(days=1)
                agent_games = [g for g in agent_games if g.end_time >= cutoff]
            elif timeframe == "weekly":
                cutoff = datetime.now() - timedelta(weeks=1)
                agent_games = [g for g in agent_games if g.end_time >= cutoff]
            
            # Create trend data
            trends = []
            running_wins = 0
            
            for i, game in enumerate(agent_games):
                if game.winner == agent_name:
                    running_wins += 1
                
                win_rate = running_wins / (i + 1) if i >= 0 else 0
                
                trend_point = {
                    'game_number': i + 1,
                    'timestamp': game.end_time.isoformat(),
                    'win_rate': win_rate,
                    'won_this_game': game.winner == agent_name,
                    'game_length': game.total_moves,
                    'opponent': self._get_opponent_name(game, agent_name)
                }
                trends.append(trend_point)
            
            return trends
            
        except Exception as e:
            print(f"⚠️ Error getting historical trends: {e}")
            return []
    
    def calculate_performance_metrics(self, timeframe: str = "all") -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics
        
        Args:
            timeframe: Time period to analyze
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            # Filter games by timeframe
            games = self.game_results
            
            if timeframe == "recent":
                games = games[-50:]  # Last 50 games
            elif timeframe == "daily":
                cutoff = datetime.now() - timedelta(days=1)
                games = [g for g in games if g.end_time >= cutoff]
            elif timeframe == "weekly":
                cutoff = datetime.now() - timedelta(weeks=1)
                games = [g for g in games if g.end_time >= cutoff]
            
            if not games:
                return {"error": "No games in specified timeframe"}
            
            # Calculate metrics
            total_games = len(games)
            total_moves = sum(g.total_moves for g in games)
            average_game_length = total_moves / total_games
            
            # Agent statistics
            agent_stats = defaultdict(lambda: {'wins': 0, 'games': 0})
            game_types = defaultdict(int)
            termination_reasons = defaultdict(int)
            
            for game in games:
                # Count game types
                game_types[game.game_id.split('_')[0] if '_' in game.game_id else 'unknown'] += 1
                
                # Count termination reasons
                termination_reasons[game.termination_reason] += 1
                
                # Update agent stats
                winner = game.winner
                if winner != "Draw" and winner != "Incomplete":
                    agent_stats[winner]['wins'] += 1
                
                # Count total games for each agent (this is simplified)
                # In a real implementation, you'd track all participants
                for agent in [winner]:  # Simplified - would need actual participant list
                    if agent not in ["Draw", "Incomplete"]:
                        agent_stats[agent]['games'] += 1
            
            # Calculate win rates
            for agent in agent_stats:
                if agent_stats[agent]['games'] > 0:
                    agent_stats[agent]['win_rate'] = agent_stats[agent]['wins'] / agent_stats[agent]['games']
            
            # Find best performing agent
            best_agent = max(agent_stats.keys(), 
                           key=lambda a: agent_stats[a]['win_rate'], 
                           default="None")
            
            metrics = {
                'timeframe': timeframe,
                'analysis_date': datetime.now().isoformat(),
                'total_games': total_games,
                'total_moves': total_moves,
                'average_game_length': average_game_length,
                'game_types': dict(game_types),
                'termination_reasons': dict(termination_reasons),
                'agent_statistics': dict(agent_stats),
                'best_performing_agent': best_agent,
                'best_win_rate': agent_stats[best_agent]['win_rate'] if best_agent != "None" else 0.0
            }
            
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error calculating performance metrics: {e}")
            return {"error": str(e)}
    
    def get_live_scores(self) -> Dict[str, float]:
        """Get current live scores"""
        return self.current_scores.copy()
    
    def get_agent_summary(self, agent_name: str) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent performance summary
        """
        try:
            if agent_name not in self.agent_performance:
                return {"error": f"Agent {agent_name} not found"}
            
            agent_data = self.agent_performance[agent_name]
            
            # Get recent performance trend
            recent_games = list(agent_data['recent_performance'])
            recent_wins = sum(1 for game in recent_games if game.get('won', False))
            recent_win_rate = recent_wins / len(recent_games) if recent_games else 0.0
            
            # Calculate performance trend
            if len(recent_games) >= 10:
                first_half = recent_games[:len(recent_games)//2]
                second_half = recent_games[len(recent_games)//2:]
                
                first_half_wins = sum(1 for game in first_half if game.get('won', False))
                second_half_wins = sum(1 for game in second_half if game.get('won', False))
                
                first_half_rate = first_half_wins / len(first_half)
                second_half_rate = second_half_wins / len(second_half)
                
                trend = "improving" if second_half_rate > first_half_rate else "declining" if second_half_rate < first_half_rate else "stable"
            else:
                trend = "insufficient_data"
            
            summary = {
                'agent_name': agent_name,
                'total_games': agent_data['total_games'],
                'wins': agent_data['wins'],
                'losses': agent_data['losses'],
                'draws': agent_data['draws'],
                'overall_win_rate': agent_data['win_rate'],
                'average_score': agent_data['average_score'],
                'recent_win_rate': recent_win_rate,
                'performance_trend': trend,
                'recent_games_count': len(recent_games),
                'last_updated': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Error getting agent summary: {e}")
            return {"error": str(e)}
    
    def get_leaderboard(self, metric: str = "win_rate", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get agent leaderboard
        
        Args:
            metric: Metric to sort by ("win_rate", "total_games", "wins")
            limit: Maximum number of agents to return
            
        Returns:
            Sorted list of agent performance data
        """
        try:
            leaderboard = []
            
            for agent_name, data in self.agent_performance.items():
                if data['total_games'] > 0:  # Only include agents with games
                    entry = {
                        'agent_name': agent_name,
                        'win_rate': data['win_rate'],
                        'total_games': data['total_games'],
                        'wins': data['wins'],
                        'average_score': data['average_score']
                    }
                    leaderboard.append(entry)
            
            # Sort by specified metric
            leaderboard.sort(key=lambda x: x.get(metric, 0), reverse=True)
            
            return leaderboard[:limit]
            
        except Exception as e:
            print(f"⚠️ Error creating leaderboard: {e}")
            return []
    
    def export_performance_report(self, output_file: str = None) -> str:
        """
        Export comprehensive performance report
        
        Args:
            output_file: Output file path (auto-generated if None)
            
        Returns:
            Path to the exported report
        """
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"performance_report_{timestamp}.json"
            
            # Generate comprehensive report
            report = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'total_games_analyzed': len(self.game_results),
                    'tracking_period': {
                        'start': self.performance_metrics['tracking_start_time'].isoformat(),
                        'end': datetime.now().isoformat()
                    }
                },
                'overall_metrics': self.calculate_performance_metrics("all"),
                'recent_metrics': self.calculate_performance_metrics("recent"),
                'agent_summaries': {
                    agent: self.get_agent_summary(agent) 
                    for agent in self.agent_performance.keys()
                },
                'leaderboard': self.get_leaderboard(),
                'game_history_sample': [
                    result.to_dict() for result in self.game_results[-10:]  # Last 10 games
                ]
            }
            
            # Save report
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, cls=HistoryEncoder)
            
            print(f"📋 Performance report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"⚠️ Error exporting performance report: {e}")
            return ""
    
    def _update_agent_performance(self, result: GameResult) -> None:
        """Update agent performance statistics"""
        try:
            # This is simplified - in reality, you'd need to track all participants
            winner = result.winner
            
            # Update winner stats
            if winner not in ["Draw", "Incomplete"]:
                perf = self.agent_performance[winner]
                perf['total_games'] += 1
                perf['wins'] += 1
                perf['total_score'] += result.final_score.get(winner, 1.0)
                perf['average_score'] = perf['total_score'] / perf['total_games']
                perf['win_rate'] = perf['wins'] / perf['total_games']
                
                # Add to recent performance
                perf['recent_performance'].append({
                    'game_id': result.game_id,
                    'won': True,
                    'score': result.final_score.get(winner, 1.0),
                    'moves': result.total_moves,
                    'timestamp': result.end_time.isoformat()
                })
            
            # Note: In a full implementation, you'd also update the loser's stats
            # This would require tracking all participants in the GameResult
            
        except Exception as e:
            print(f"⚠️ Error updating agent performance: {e}")
    
    def _update_performance_metrics(self, result: GameResult) -> None:
        """Update overall performance metrics"""
        try:
            self.performance_metrics['total_games_tracked'] += 1
            self.performance_metrics['total_moves_tracked'] += result.total_moves
            
            # Update average game length
            total_games = self.performance_metrics['total_games_tracked']
            total_moves = self.performance_metrics['total_moves_tracked']
            self.performance_metrics['average_game_length'] = total_moves / total_games
            
            # Update most active agent (simplified)
            if result.winner not in ["Draw", "Incomplete"]:
                current_best = self.performance_metrics.get('best_performing_agent', '')
                if not current_best or (result.winner in self.agent_performance and 
                                      self.agent_performance[result.winner]['win_rate'] > 
                                      self.agent_performance.get(current_best, {}).get('win_rate', 0)):
                    self.performance_metrics['best_performing_agent'] = result.winner
            
        except Exception as e:
            print(f"⚠️ Error updating performance metrics: {e}")
    
    def _get_opponent_name(self, game: GameResult, agent_name: str) -> str:
        """Get opponent name from game result"""
        # This is simplified - would need better participant tracking
        if game.winner == agent_name:
            return "Unknown"  # Would need actual opponent tracking
        else:
            return game.winner if game.winner not in ["Draw", "Incomplete"] else "Unknown"
    
    def _load_history(self) -> None:
        """Load historical data from disk"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                
                # Load game results
                if 'game_results' in data:
                    self.game_results = [
                        GameResult.from_dict(result_data) 
                        for result_data in data['game_results']
                    ]
                
                # Load agent performance
                if 'agent_performance' in data:
                    for agent, perf_data in data['agent_performance'].items():
                        self.agent_performance[agent].update(perf_data)
                        # Convert recent_performance back to deque
                        if 'recent_performance' in perf_data:
                            self.agent_performance[agent]['recent_performance'] = deque(
                                perf_data['recent_performance'], maxlen=20
                            )
                
                # Load performance metrics
                if 'performance_metrics' in data:
                    self.performance_metrics.update(data['performance_metrics'])
                    # Convert tracking_start_time back to datetime
                    if 'tracking_start_time' in self.performance_metrics:
                        self.performance_metrics['tracking_start_time'] = datetime.fromisoformat(
                            self.performance_metrics['tracking_start_time']
                        )
                
                print(f"📊 Loaded {len(self.game_results)} historical games")
            
        except Exception as e:
            print(f"⚠️ Error loading history: {e}")
    
    def _save_history(self) -> None:
        """Save historical data to disk"""
        try:
            # Prepare data for serialization
            data = {
                'game_results': [result.to_dict() for result in self.game_results],
                'agent_performance': {},
                'performance_metrics': self.performance_metrics.copy(),
                'last_saved': datetime.now().isoformat()
            }
            
            # Convert agent performance data
            for agent, perf in self.agent_performance.items():
                data['agent_performance'][agent] = dict(perf)
                # Convert deque to list for JSON serialization
                data['agent_performance'][agent]['recent_performance'] = list(perf['recent_performance'])
            
            # Convert datetime in performance_metrics
            if 'tracking_start_time' in data['performance_metrics']:
                data['performance_metrics']['tracking_start_time'] = data['performance_metrics']['tracking_start_time'].isoformat()
            
            # Save to file
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2, cls=HistoryEncoder)
            
        except Exception as e:
            print(f"⚠️ Error saving history: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Save final state
        self._save_history()
        print("📊 ScoreTracker cleanup completed")