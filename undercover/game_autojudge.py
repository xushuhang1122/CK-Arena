import json
import datetime
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from undercover.player import Player
from undercover.judge import Judge
from time import time

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
            
            # Use two specialized judges to evaluate reasonableness and novelty
            # Assuming we have exactly 2 judges: one for reasonableness and one for novelty
            reasonableness_judge = self.judges[0]  # First judge evaluates reasonableness
            novelty_judge = self.judges[1]         # Second judge evaluates novelty
            
            another_concept = self.civilian_concept if player.assigned_concept == self.undercover_concept else self.undercover_concept
            
            # Get binary decisions (0/1) from specialized judges
            # 1 means player should be eliminated, 0 means continue
            reasonableness_eliminate = self._judge_reasonableness(
                reasonableness_judge,
                self.statement_history,
                statement_content, 
                player.assigned_concept,
                another_concept
            )
            
            novelty_eliminate = self._judge_novelty(
                novelty_judge,
                self.statement_history,
                statement_content, 
                player.assigned_concept,
                another_concept
            )
            
            # Player should be eliminated if either judge says so
            should_eliminate = bool(reasonableness_eliminate) or bool(novelty_eliminate)
            elimination_reason = None
            
            if should_eliminate:
                if reasonableness_eliminate:
                    elimination_reason = "Low reasonableness"
                if novelty_eliminate:
                    if elimination_reason:
                        elimination_reason += " and low novelty"
                    else:
                        elimination_reason = "Low novelty"

            # Store judge evaluations
            metrics = {
                "judges_evaluations": [
                    {
                        "judge_id": self.judges[0].judge_id if len(self.judges) > 0 else "reasonableness_judge",
                        "type": "reasonableness",
                        "eliminate": reasonableness_eliminate
                    },
                    {
                        "judge_id": self.judges[1].judge_id if len(self.judges) > 1 else "novelty_judge",
                        "type": "novelty",
                        "eliminate": novelty_eliminate
                    }
                ],
                "judges_stats": None  # No longer calculating scores
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
                        "reasonableness_eliminate": reasonableness_eliminate,
                        "novelty_eliminate": novelty_eliminate
                    }
                }
                
                self.game_record["game_process"]["metric_eliminations"].append(eliminated_info)
                self.statement_history += f"Player_{player.player_id} was eliminated due to: {elimination_reason}\n"
                
                # After each elimination, check if the game should end
                if self._check_win_conditions():
                    self.game_over = True
                    return False
            
        return True

    def _judge_reasonableness(self, judge, statement_history: str, statement_content: str, 
                            assigned_concept: str, another_concept: str) -> int:
        """
        Judge if a statement is reasonable (1 = eliminate, 0 = continue)
        This function should be implemented by you
        
        Returns:
            int: 1 if player should be eliminated for unreasonableness, 0 otherwise
        """
        def call_bailian_api(
            input_messages: Optional[List[Dict]] = None,
            temperature: float = 0.4,
            model: str = '',
            max_tokens: int = 256,
            stream: bool = False
        ):

            MAX_RETRIES = 12
            attempts = 0
            RETRY_INTERVAL = 1

            while attempts < MAX_RETRIES:
                try:
                    client = OpenAI(
                        api_key="",
                        base_url="",
                    )
                    completion = client.chat.completions.create(
                        model=model,
                        messages=input_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream,
                        extra_body={"enable_thinking": False}
                    )

                    if stream:
                        content = ""
                        for chunk in completion:
                            if chunk.choices[0].delta.content:
                                content += chunk.choices[0].delta.content
                        return content.strip()
                    else:
                        return completion.choices[0].message.content.strip()

                except Exception as e:
                    if attempts < MAX_RETRIES - 1:
                        print(f"HTTP Exception or Timeout Error occurred: {e}. Retrying in {RETRY_INTERVAL} seconds...")
                        time.sleep(RETRY_INTERVAL)
                        attempts += 1
                        RETRY_INTERVAL *= 2
                    else:
                        raise Exception(f"Failed to get response after {MAX_RETRIES} attempts.") from e
        
        try:
            messages = [
                {"role": "system", "content": "You will receive a word and a descriptive sentence, please judge whether this sentence is reasonable for describing the word."},
                {"role": "user", "content": f"\nWhat needs to be judged:\nWord: {assigned_concept}\nSentence: {statement_content}"}
            ]

            response_text = call_bailian_api(input_messages=messages, stream=False)
            # response 1 means reasonable, then should return 0 which means no need to eliminate

            
            for char in response_text:
                if char.isdigit():
                    result = int(char)
                    return 0 if result >= 1 else 1
            
            
            return 0
            
        except Exception as e:
            
            return 0

    def _judge_novelty(self, judge, statement_history: str, statement_content: str, 
                    assigned_concept: str, another_concept: str) -> int:
        """
        Judge if a statement has sufficient novelty (1 = eliminate, 0 = continue)
        This function should be implemented by you
        
        Returns:
            int: 1 if player should be eliminated for low novelty, 0 otherwise
        """
        try:
            historical_statements = []
            if statement_history:
                lines = statement_history.strip().split('\n')
                for line in lines:
                    if line.startswith('Player_') and ':' in line:
                        
                        statement = line.split(':', 1)[1].strip()
                        if statement:
                            historical_statements.append(statement)
            
            
            if not historical_statements:
                return 0
                
            
            
            all_statements = historical_statements + [statement_content]
            
            
            embeddings = []
            batch_size = 10
            for i in range(0, len(all_statements), batch_size):
                batch_texts = all_statements[i:i+batch_size]
                try:
                    client = OpenAI(
                        api_key="",
                        base_url=""
                    )
                    completion = client.embeddings.create(
                        model="text-embedding-v4",
                        input=batch_texts,
                        dimensions=1024,
                        encoding_format="float"
                    )

                    for data in completion.data:
                        embeddings.append(np.array(data.embedding))
                except Exception as e:
                    
                    return 0
            
            if len(embeddings) != len(all_statements):
                return 0
                

            historical_embeddings = embeddings[:-1]
            current_embedding = embeddings[-1]
            

            similarity_threshold = 0.5 
            for hist_embedding in historical_embeddings:
                
                dot_product = np.dot(current_embedding, hist_embedding)
                norm_current = np.linalg.norm(current_embedding)
                norm_hist = np.linalg.norm(hist_embedding)
                
                if norm_current > 0 and norm_hist > 0:
                    cosine_similarity = dot_product / (norm_current * norm_hist)
                    
                   
                    if cosine_similarity > similarity_threshold:
                        return 1  
                        
            return 0  
            
        except Exception as e:
            return 0




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