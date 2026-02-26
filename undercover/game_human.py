import json
import datetime
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from undercover.player import Player
from undercover.judge import Judge
from undercover.agents.human_player import HumanPlayer
from time import time

class UndercoverHumanGame:
    """
    Main class for the Undercover game with human player support
    Extends the original game logic to handle mixed human and AI players
    """

    def __init__(self,
                 topic_category: str,
                 concept_pair: Tuple[str, str],
                 judges: List[Judge],
                 players: List[Player],
                 civilian_count: int = 4,
                 undercover_count: int = 2,
                 max_statement_rounds: int = 10,
                 statements_per_voting: int = 1):
        """
        Initialize the game with human player support

        Parameters:
            topic_category: Category of the topic
            concept_pair: Tuple of (civilian concept, undercover concept)
            judges: List of judge objects
            players: List of player objects (can include HumanPlayer instances)
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
        self.statements_per_voting = statements_per_voting

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

        # Human player specific
        self.human_players = [p for p in self.players if isinstance(p, HumanPlayer)]
        self.ai_players = [p for p in self.players if not isinstance(p, HumanPlayer)]

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

        # Call set_game_start_info for human players after role assignment
        for player in self.players:
            if isinstance(player, HumanPlayer):
                player.set_game_start_info(len(self.players))

        # Record player information
        for player in self.players:
            self.game_record["players"].append(player.to_dict())

    def run_game(self):
        """Run the game logic with human player support"""
        self.setup_game()

        # Display game setup information
        print(f"\n[GAME] === GAME START ===")
        print(f"[INFO] Topic: {self.topic_category}")
        print(f"[INFO] Players: {len(self.players)} total ({self.civilian_count} civilians, {self.undercover_count} undercovers)")
        print(f"[INFO] Max Rounds: {self.max_statement_rounds}")
        print(f"[INFO] Evaluation: Automated (reasonableness + novelty)")
        print("=" * 60)

        while not self.game_over:
            # Phase 1: Statement Rounds
            for round_number in range(1, self.statements_per_voting + 1):
                self.current_statement_round += 1

                if self.current_statement_round > self.max_statement_rounds:
                    self.game_over = True
                    break

                # Display round start information
                print(f"\n[ROUND] === ROUND {self.current_statement_round} ===")
                active_players = [p for p in self.players if not p.eliminated]
                print(f"[STATUS] Active Players: {len(active_players)} | Statement Phase")
                print("-" * 60)

                # Conduct one complete round of statements
                if not self._conduct_statement_round():
                    break  # Game ended during statements

                # Update round history after each round
                self._update_round_history(self.current_statement_round)

            # Phase 2: Voting Round
            if not self.game_over:
                # Display voting round information
                active_players = [p for p in self.players if not p.eliminated]
                print(f"\n[VOTING] === VOTING ROUND {self.current_voting_round + 1} ===")
                print(f"[STATUS] Active Players: {len(active_players)} | Time to vote!")
                print(f"[ACTION] Each player will vote for who they think is the UNDERCOVER!")
                print("-" * 60)

                self._conduct_voting_round()

            # Check if game should end
            if self._check_win_conditions():
                self.game_over = True
                break

            # Check if we've reached max rounds
            if self.current_statement_round >= self.max_statement_rounds:
                self.game_over = True
                break

        # Game over, show results and update game record
        self._display_game_results()
        self._update_game_record()

    def _conduct_statement_round(self) -> bool:
        """
        Conduct one complete round of statements with human player support

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

            # Human player special handling
            if isinstance(player, HumanPlayer):
                print(f"\n[TURN] === YOUR TURN ===")
                print(f"[INFO] Your concept: {player.assigned_concept}")
                print(f"[INFO] Previous statements to consider:")
                if self.statement_history.strip():
                    lines = self.statement_history.strip().split('\n')[-3:]  # Show last 3 statements
                    for line in lines:
                        if line.startswith('Player_') and ':' in line:
                            statement = line.split(':', 1)[1].strip()
                            print(f"   - {statement}")
                print(f"[ACTION] Make your statement (be creative but clear!):")

            # Player generates a statement
            statement_content = player.generate_statement(self.statement_history)

            # Display player statement
            if isinstance(player, HumanPlayer):
                player_type = "[YOU]"
            else:
                player_type = f"[AI] Player {player.player_id}"

            print(f"\n[SPEECH] {player_type} says:")
            print(f"   \"{statement_content}\"")
            print("-" * 60)

            # Use automated evaluation (binary decisions) instead of LLM judges
            another_concept = self.civilian_concept if player.assigned_concept == self.undercover_concept else self.undercover_concept

            # Use two specialized judges to evaluate reasonableness and novelty
            reasonableness_judge = self.judges[0]  # First judge evaluates reasonableness
            novelty_judge = self.judges[1]         # Second judge evaluates novelty

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

                # Host announcement for elimination
                if isinstance(player, HumanPlayer):
                    player_type = "[YOU]"
                else:
                    player_type = f"[AI] Player {player.player_id}"

                print(f"\n[ELIMINATION] === PLAYER ELIMINATED ===")
                print(f"[INFO] {player_type} has been eliminated by evaluation!")
                print(f"[INFO] Reason: {elimination_reason}")
                print(f"[INFO] Game continues...")

                print("=" * 60)

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

            # Small delay for better human experience
            if player in self.ai_players:
                import time
                time.sleep(1)

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
        """Update the round history with statements from the specified round"""
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

        # Display voting results
        if isinstance(eliminated_player, HumanPlayer):
            player_type = "[YOU]"
        else:
            player_type = f"[AI] Player {eliminated_player.player_id}"

        print(f"\n[VOTE_RESULT] === VOTING RESULTS ===")
        print(f"[INFO] {player_type} has been voted out!")
        print(f"[INFO] Votes received: {vote_counts[eliminated_id]}")

        # Show voting breakdown
        print(f"\n[VOTE_BREAKDOWN] === VOTING BREAKDOWN ===")
        for vote in votes:
            # Find the voter player object to determine if it's human
            voter_player = next((p for p in self.players if p.player_id == vote["voter_id"]), None)
            if voter_player and isinstance(voter_player, HumanPlayer):
                voter_type = "[YOU]"
            else:
                voter_type = f"[AI] Player {vote['voter_id']}"

            # Find the voted player object to determine if it's human
            voted_player = next((p for p in self.players if p.player_id == vote["voted_for"]), None)
            if voted_player and isinstance(voted_player, HumanPlayer):
                voted_type = "[YOURSELF]"
            else:
                voted_type = f"[AI] Player {vote['voted_for']}"

            print(f"   {voter_type} → voted for {voted_type}")

        if isinstance(eliminated_player, HumanPlayer):
            print("\n[GAME_OVER] You've been voted out! Thanks for playing.")
            print("[RESULT] The game continues without you...")

        print("=" * 60)

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

    def _display_game_results(self):
        """Display final game results to human player"""
        print(f"\n[GAME_OVER] === GAME OVER ===")

        if self.winner_role == "civilian":
            print("[WINNER] === CIVILIANS WIN! ===")
            print("[INFO] All undercovers have been eliminated!")
        elif self.winner_role == "undercover":
            print("[WINNER] === UNDERCOVERS WIN! ===")
            print("[INFO] Undercovers now equal or outnumber civilians!")

        print("\n[FINAL_STATUS] === FINAL PLAYER STATUS ===")
        for player in self.players:
            if isinstance(player, HumanPlayer):
                status_marker = "[WINNER]" if player.is_winner else "[ELIMINATED]"
                role_marker = "[UNDERCOVER]" if player.role == "undercover" else "[CIVILIAN]"
                print(f"   [YOU] {role_marker}: {player.role.upper()} - {status_marker}")
            else:
                status_marker = "[WINNER]" if player.is_winner else "[ELIMINATED]"
                role_marker = "[UNDERCOVER]" if player.role == "undercover" else "[CIVILIAN]"
                print(f"   [AI] Player {player.player_id} {role_marker}: {player.role.upper()} - {status_marker}")
                print(f"        (LLM: {player.llm_id})")  # Only show LLM info at game end

        print("\n[STATS] === GAME STATISTICS ===")
        print(f"[INFO] Total Rounds: {self.current_statement_round}")
        print(f"[INFO] Total Statements: {len(self.statements)}")

        correct_eliminations = sum(
            1 for round_info in self.voting_rounds
            for elim in round_info["eliminated"]
            if elim["correct_elimination"]
        )
        incorrect_eliminations = sum(
            1 for round_info in self.voting_rounds
            for elim in round_info["eliminated"]
            if not elim["correct_elimination"]
        )

        print(f"[INFO] Correct Eliminations: {correct_eliminations}")
        print(f"[INFO] Incorrect Eliminations: {incorrect_eliminations}")

        print("=" * 60)

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

    def _judge_reasonableness(self, judge, statement_history: str, statement_content: str,
                            assigned_concept: str, another_concept: str) -> int:
        """
        Judge if a statement is reasonable (1 = eliminate, 0 = continue)

        Returns:
            int: 1 if player should be eliminated for unreasonableness, 0 otherwise
        """
        def call_bailian_api(
            input_messages: Optional[List[Dict]] = None,
            temperature: float = 0.4,
            model: str = 'qwen3-8b-ft-202509101557-4279',
            max_tokens: int = 256,
            stream: bool = False
        ):
            """
            调用百炼API
            """
            MAX_RETRIES = 12
            attempts = 0
            RETRY_INTERVAL = 1

            while attempts < MAX_RETRIES:
                try:
                    client = OpenAI(
                        api_key="sk-4e354bbbd12a4a02b4c05827a6fe9f59",
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
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

            # 提取第一个数字作为结果
            for char in response_text:
                if char.isdigit():
                    result = int(char)
                    # 确保结果是0或1
                    return 0 if result >= 1 else 1

            # 如果无法解析出数字，默认返回0（不淘汰）
            return 0

        except Exception as e:
            # 如果出现任何错误，保守地返回0（不淘汰）
            return 0

    def _judge_novelty(self, judge, statement_history: str, statement_content: str,
                    assigned_concept: str, another_concept: str) -> int:
        """
        Judge if a statement has sufficient novelty (1 = eliminate, 0 = continue)

        Returns:
            int: 1 if player should be eliminated for low novelty, 0 otherwise
        """
        try:
            # 提取历史陈述（从statement_history中解析）
            # 假设历史陈述格式为 "Player_X: statement content"
            historical_statements = []
            if statement_history:
                lines = statement_history.strip().split('\n')
                for line in lines:
                    if line.startswith('Player_') and ':' in line:
                        # 提取陈述内容（冒号后的部分）
                        statement = line.split(':', 1)[1].strip()
                        if statement and statement not in ["Low novelty", "Low reasonableness"]:
                            historical_statements.append(statement)

            # Remove debug output for cleaner gameplay
            # DEBUG: 输出novelty判断信息
            # print(f"[DEBUG] === NOVELTY EVALUATION ===")
            # print(f"[DEBUG] Current statement: \"{statement_content}\"")
            # print(f"[DEBUG] Historical statements found: {len(historical_statements)}")
            # for i, hist in enumerate(historical_statements):
            #     print(f"[DEBUG]   {i+1}. \"{hist}\"")

            # 如果没有历史陈述，则认为是新颖的
            if not historical_statements:
                return 0

            # 为当前陈述和历史陈述生成嵌入向量
            # 将当前陈述与所有历史陈述一起处理以保持一致性
            all_statements = historical_statements + [statement_content]

            # 生成嵌入向量
            embeddings = []
            batch_size = 10
            for i in range(0, len(all_statements), batch_size):
                batch_texts = all_statements[i:i+batch_size]
                try:
                    client = OpenAI(
                        api_key="sk-4e354bbbd12a4a02b4c05827a6fe9f59",
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
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
                    # 如果API调用失败，回退到简单的文本比较
                    return 0

            if len(embeddings) != len(all_statements):
                return 0

            # 分离历史嵌入和当前陈述嵌入
            historical_embeddings = embeddings[:-1]
            current_embedding = embeddings[-1]

            # 计算当前陈述与历史陈述的相似度
            similarity_threshold = 0.85  # 提高相似度阈值，更宽松的新颖性标准
            max_similarity = 0.0
            similarity_count = 0

            for i, hist_embedding in enumerate(historical_embeddings):
                # 计算余弦相似度
                dot_product = np.dot(current_embedding, hist_embedding)
                norm_current = np.linalg.norm(current_embedding)
                norm_hist = np.linalg.norm(hist_embedding)

                if norm_current > 0 and norm_hist > 0:
                    cosine_similarity = dot_product / (norm_current * norm_hist)
                    max_similarity = max(max_similarity, cosine_similarity)
                    similarity_count += 1

                else:
                    continue

            # 只有当相似度超过阈值且比较次数足够时，才认为缺乏新颖性
            # 如果历史陈述少于2个，则更宽松地判断
            if similarity_count >= 2 and max_similarity > similarity_threshold:
                return 1  # 缺乏新颖性，应该淘汰
            elif similarity_count == 1 and max_similarity > 0.85:  # 单个历史陈述时，需要更高相似度
                return 1  # 与单个陈述高度相似，应该淘汰

            return 0  # 具有新颖性，继续游戏

        except Exception as e:
            # 如果出现任何错误，保守地返回0（不淘汰）
            return 0

    def save_game_record(self, filename: str):
        """Save the game record to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.get_game_record(), f, ensure_ascii=False, indent=2)