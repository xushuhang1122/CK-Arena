import json
import datetime
import random
from typing import List, Dict, Any, Optional, Tuple

from undercover.player import Player
from undercover.judge import Judge

class UndercoverGame:
    """Main class for the Undercover game"""
    
    def __init__(self, 
                 topic_category: str,
                 concept_pair: Tuple[str, str],
                 judges: List[Judge],
                 players: List[Player],
                 civilian_count: int = 3,
                 undercover_count: int = 1,
                 max_statement_rounds: int = 10,
                 statements_per_voting: int = 1):
        """
        Initialize the game
        
        Parameters:
            topic_category: Category of the topic
            concept_pair: Tuple of (civilian concept, undercover concept)
            judges: List of judge objects
            players: List of player objects
            civilian_count: Number of civilian players
            undercover_count: Number of undercover players
            max_statement_rounds: Maximum number of statement rounds
            statements_per_voting: Number of complete statement rounds before each voting
        """
        self.game_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.timestamp = datetime.datetime.now().isoformat()
        self.topic_category = topic_category
        self.civilian_concept, self.undercover_concept = concept_pair
        self.judges = judges
        
        self.players = players
        self.civilian_count = civilian_count
        self.undercover_count = undercover_count
        self.max_statement_rounds = max_statement_rounds
        self.statements_per_voting = statements_per_voting  # Now represents complete rounds before voting
        
        # Game state
        self.current_statement_round = 0
        self.current_voting_round = 0
        self.statements = []
        self.voting_rounds = []
        self.game_over = False
        self.winner_role = None
        
        # Game history by round for LLM context
        self.round_history = {}
        self.statement_history = ""
        
        # Initialize game record
        self.game_record = self._initialize_game_record()
        
    def _initialize_game_record(self) -> Dict[str, Any]:
        """Initialize the game record"""
        return {
            "game_id": self.game_id,
            "timestamp": self.timestamp,
            "topic_category": self.topic_category,
            "concept_pair": {
                "concept_a": self.civilian_concept,
                "concept_b": self.undercover_concept
            },
            "judges": [judge.to_dict() for judge in self.judges],
            "players": [],  # Will be populated after role assignment
            "game_process": {
                "statements": [],
                "voting_rounds": []
            },
            "game_summary": {},  # Will be populated after game ends
            "game_analysis": {}  # Will be populated after game ends
        }
        
    def setup_game(self):
        """Set up the game, assign roles and concepts"""
        if len(self.players) < self.civilian_count + self.undercover_count:
            raise ValueError("Not enough players")
            
        # Randomly select civilians and undercovers
        all_indices = list(range(len(self.players)))
        random.shuffle(all_indices)
        
        civilian_indices = all_indices[:self.civilian_count]
        undercover_indices = all_indices[self.civilian_count:self.civilian_count + self.undercover_count]
        
        # Assign roles and concepts
        for i, player in enumerate(self.players):
            if i in civilian_indices:
                player.assign_role("civilian", self.civilian_concept)
            elif i in undercover_indices:
                player.assign_role("undercover", self.undercover_concept)
            
            # Record player information
            self.game_record["players"].append(player.to_dict())
            
    def run_game(self):
        """Run the game logic"""
        self.setup_game()
        
        while not self.game_over:
            # Phase 1: Statement Rounds
            for round_number in range(1, self.statements_per_voting + 1):
                self.current_statement_round += 1
                
                if self.current_statement_round > self.max_statement_rounds:
                    self.game_over = True
                    break
                
                # Conduct one complete round of statements
                if not self._conduct_statement_round():
                    break  # Game ended during statements
                
                # Update round history after each round
                self._update_round_history(self.current_statement_round)
            
            # Phase 2: Voting Round
            if not self.game_over:
                self._conduct_voting_round()
            
            # Check if game should end
            if self._check_win_conditions():
                self.game_over = True
                break
                
            # Check if we've reached max rounds
            if self.current_statement_round >= self.max_statement_rounds:
                self.game_over = True
                break
        
        # Game over, update game record
        self._update_game_record()
    
    def _conduct_statement_round(self) -> bool:
        """
        Conduct one complete round of statements where all active players make a statement
        
        Returns:
            bool: True if the round completed normally, False if the game ended
        """
        active_players = [p for p in self.players if not p.eliminated]
        random.shuffle(active_players)
        self.statement_history += f"\n\nRound {self.current_statement_round}:\n\n"
        
        # Keep track of players eliminated during this round
        players_eliminated_this_round = []
        
        for player in active_players:
            # Skip players eliminated during this round
            if player in players_eliminated_this_round:
                continue
                
            # Build current game state for player reference
            game_state = self._build_game_state()
            
            # Player generates a statement
            statement_content = player.generate_statement(self.statement_history)
            
            # Judge evaluates the statement
            all_judges_metrics = []
            judges_evaluations = []
            another_concept = self.civilian_concept if player.assigned_concept == self.undercover_concept else self.undercover_concept

            for judge in self.judges:
                # Get the three scores from evaluate_statement
                novelty_score, relevance_score, reasonableness_score = judge.evaluate_statement(
                    self.statement_history,
                    statement_content, 
                    player.assigned_concept,
                    another_concept
                )
                
                # Convert to dictionary format for compatibility
                judge_metrics = {
                    "novelty_score": novelty_score,
                    "relevance_score": relevance_score,
                    "reasonableness_score": reasonableness_score
                }
                
                # Store judge evaluation with ID
                judge_evaluation = {
                    "judge_id": judge.judge_id,
                    "metrics": judge_metrics
                }
                
                all_judges_metrics.append(judge_metrics)
                judges_evaluations.append(judge_evaluation)

            # Calculate mean and variance for each metric across all judges
            metrics_stats = {}

            if all_judges_metrics:
                # Process each metric type
                for metric_name in ["novelty_score", "relevance_score", "reasonableness_score"]:
                    scores = [judge_metrics[metric_name] for judge_metrics in all_judges_metrics]
                    
                    if scores:
                        # Calculate mean score
                        mean_score = sum(scores) / len(scores)
                        
                        # Calculate variance
                        if len(scores) > 1:
                            variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
                        else:
                            variance = 0
                        
                        # Store stats
                        metrics_stats[f"{metric_name}_mean"] = mean_score
                        metrics_stats[f"{metric_name}_variance"] = variance
                        metrics_stats[f"{metric_name}_all_values"] = {
                            judge_eval["judge_id"]: judge_eval["metrics"][metric_name]
                            for judge_eval in judges_evaluations
                        }

            # Check if player should be eliminated based on low novelty or reasonableness
            novelty_mean = metrics_stats.get("novelty_score_mean", 1.0)
            reasonableness_mean = metrics_stats.get("reasonableness_score_mean", 1.0)
            
            should_eliminate = novelty_mean <= 0.3 or reasonableness_mean <= 0.3
            elimination_reason = None
            
            if should_eliminate:
                if novelty_mean < 0.3:
                    elimination_reason = f"Low novelty score: {novelty_mean:.2f}"
                if reasonableness_mean < 0.3:
                    if elimination_reason:
                        elimination_reason += f" and low reasonableness score: {reasonableness_mean:.2f}"
                    else:
                        elimination_reason = f"Low reasonableness score: {reasonableness_mean:.2f}"

            # Store all judges' evaluations and stats
            metrics = {
                "judges_evaluations": judges_evaluations,
                "judges_stats": metrics_stats
            }

            # Record the statement
            statement_id = len(self.statements) + 1
            statement = {
                "statement_id": statement_id,
                "player_id": player.player_id,
                "llm_id": player.llm_id,
                "content": statement_content,
                "statement_round": self.current_statement_round,
                "metrics": metrics,
            }
            
            self.statements.append(statement)
            self.game_record["game_process"]["statements"].append(statement)
            self.statement_history += f"Player_{player.player_id}: {statement_content}\n"
            
            # Eliminate player if necessary
            if should_eliminate:
                player.eliminate(-1)
                players_eliminated_this_round.append(player)
                
                # Record the elimination in a special "metric_elimination" list
                if "metric_eliminations" not in self.game_record["game_process"]:
                    self.game_record["game_process"]["metric_eliminations"] = []
                    
                eliminated_info = {
                    "player_id": player.player_id,
                    "llm_id": player.llm_id,
                    "role": player.role,
                    "elimination_round": self.current_statement_round,
                    "elimination_reason": elimination_reason,
                    "metrics": {
                        "novelty_mean": novelty_mean,
                        "reasonableness_mean": reasonableness_mean
                    }
                }
                
                self.game_record["game_process"]["metric_eliminations"].append(eliminated_info)
                self.statement_history += f"Player_{player.player_id} was eliminated due to: {elimination_reason}\n"
                
                # After each elimination, check if the game should end
                if self._check_win_conditions():
                    self.game_over = True
                    return False
            
        return True
    
    def _check_win_conditions(self) -> bool:
        """Check if the game should end based on win conditions"""
        active_players = [p for p in self.players if not p.eliminated]
        civilian_players = [p for p in active_players if p.role == "civilian"]
        undercover_players = [p for p in active_players if p.role == "undercover"]
        
        if len(civilian_players) == len(undercover_players):
            # Undercover wins
            self.winner_role = "undercover"
            for player in self.players:
                if player.role == "undercover":
                    player.set_as_winner()
            return True
            
        if len(undercover_players) == 0:
            # Civilian wins
            self.winner_role = "civilian"
            for player in self.players:
                if player.role == "civilian":
                    player.set_as_winner()
            return True
            
        return False
    
    def _build_game_state(self) -> Dict[str, Any]:
        """Build the current game state"""
        return {
            "current_statement_round": self.current_statement_round,
            "current_voting_round": self.current_voting_round,
            "statements": self.statements,
            "voting_rounds": self.voting_rounds,
            "active_players": [p.player_id for p in self.players if not p.eliminated],
            "round_history": self.round_history
        }
    
    def _update_round_history(self, round_number: int):
        """
        Update the round history with statements from the specified round
        
        Parameters:
            round_number: The round number to update
        """
        round_statements = [s for s in self.statements if s["statement_round"] == round_number]
        
        # Format history for this round
        round_history = {
            "round_number": round_number,
            "statements": []
        }
        
        for statement in round_statements:
            player_id = statement["player_id"]
            player = next((p for p in self.players if p.player_id == player_id), None)
            
            if player:
                round_history["statements"].append({
                    "player_id": player_id,
                    "llm_id": player.llm_id,
                    "content": statement["content"]
                })
        
        # Add voting information if available for this round
        # Note: Now we check if voting happened after all statement rounds
        if round_number % self.statements_per_voting == 0:
            matching_voting_rounds = [vr for vr in self.voting_rounds 
                                   if vr["after_statement_round"] == round_number]
            
            if matching_voting_rounds:
                round_history["voting"] = matching_voting_rounds[0]
        
        # Update the round history
        self.round_history[round_number] = round_history
        
    def _conduct_voting_round(self):
        """Conduct a voting round where all active players vote"""
        self.current_voting_round += 1
        active_players = [p for p in self.players if not p.eliminated]
        
        # Collect votes from all players
        votes = []
        vote_counts = {p.player_id: 0 for p in active_players}
        
        for voter in active_players:
            game_state = self._build_game_state()
            voted_id = voter.vote(self.statement_history, active_players)
            
            # Record the vote
            votes.append({
                "voter_id": voter.player_id,
                "voted_for": voted_id
            })
            
            # Count votes
            vote_counts[voted_id] = vote_counts.get(voted_id, 0) + 1
            
        # Find the player with the most votes
        valid_vote_counts = {player_id: count for player_id, count in vote_counts.items() 
                    if any(p.player_id == player_id for p in active_players)}
        max_votes = max(valid_vote_counts.values())
        most_voted_ids = [player_id for player_id, count in valid_vote_counts.items() if count == max_votes]
        
        # If there's a tie, randomly select one
        eliminated_id = random.choice(most_voted_ids)
        
        eliminated_player = None
        for p in active_players:
            if p.player_id == eliminated_id:
                eliminated_player = p
                break

        eliminated_player.eliminate(self.current_voting_round)

        # Determine if the elimination was correct
        correct_elimination = eliminated_player.role == "undercover"
        
        # Record the eliminated player
        eliminated_info = {
            "player_id": eliminated_player.player_id,
            "llm_id": eliminated_player.llm_id,
            "role": eliminated_player.role,
            "correct_elimination": correct_elimination
        }
        
        # Record the voting round
        last_statement = self.statements[-1]
        voting_round = {
            "voting_round_id": self.current_voting_round,
            "after_statement_round": self.current_statement_round,
            "after_statement_id": last_statement["statement_id"],
            "votes": votes,
            "vote_results": valid_vote_counts,
            "eliminated": [eliminated_info]
        }
        
        self.voting_rounds.append(voting_round)
        self.game_record["game_process"]["voting_rounds"].append(voting_round)
        
    def _update_game_record(self):
        """Update the game record, adding summary and analysis"""
        # Update player information
        self.game_record["players"] = [player.to_dict() for player in self.players]
        
        # Game summary
        winner_ids = [p.player_id for p in self.players if p.is_winner]
        correct_identifications = sum(
            1 for round_info in self.voting_rounds 
            for elim in round_info["eliminated"] 
            if elim["correct_elimination"]
        )
        incorrect_identifications = sum(
            1 for round_info in self.voting_rounds 
            for elim in round_info["eliminated"] 
            if not elim["correct_elimination"]
        )
        
        self.game_record["game_summary"] = {
            "total_statement_rounds": self.current_statement_round,
            "total_voting_rounds": self.current_voting_round,
            "total_statements": len(self.statements),
            "winner_role": self.winner_role,
            "winner_ids": winner_ids,
            "correct_identifications": correct_identifications,
            "incorrect_identifications": incorrect_identifications,
            "game_decision_quality": correct_identifications / (correct_identifications + incorrect_identifications) if (correct_identifications + incorrect_identifications) > 0 else 0
        }
    
    def get_game_record(self) -> Dict[str, Any]:
        """Get the complete game record"""
        return {"game_record": self.game_record}
    
    def save_game_record(self, filename: str):
        """Save the game record to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_game_record(), f, ensure_ascii=False, indent=2)