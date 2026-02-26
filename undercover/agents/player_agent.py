import random
import json
from typing import List, Dict, Any, Optional, Tuple

from undercover.player import Player
from undercover.agents.utils import call_api, llm_set
from undercover.agents.json_validator import safe_parse_json

class LLMPlayer(Player):
    """
    LLM-based player implementation
    Uses an LLM to generate statements and voting decisions
    """
    def __init__(self, player_id: int, llm_id: str, language: str):
        super().__init__(player_id, llm_id, language)
        if language == "zh":
            from undercover.agents.prompts import player_prompt_zh
            self.prompt = player_prompt_zh
        elif language == "en":
            from undercover.agents.prompts import player_prompt_en
            self.prompt = player_prompt_en
        elif language == "fr":
            from undercover.agents.prompts import player_prompt_fr
            self.prompt = player_prompt_fr
    def generate_statement(self, statement_history) -> str:
        """
        Call LLM API to generate a description
        
        Parameters:
            statement_history: All statements in this game
            statement_round: Current statement round
            
        Returns:
            str: Player's statement
        """
        # Use round history from game state if available
        # statement_history = game_state.get("statement_history", {})
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                llm_info = {
                    "model": self.llm_id,
                    "temperature": llm_set["temperature"],
                    "max_tokens": llm_set["max_tokens"],
                    "input_messages": [
                        {"role": "system", "content": self.prompt.system_speak_player()},
                        {"role": "user", "content": self.prompt.user_speak_player(self.player_id, self.assigned_concept, statement_history, self.last_analyze, "")}
                    ]
                }

                """
                ======================= PROMPT =======================
                User input (4 neccesary): 
                player_id, assigned_concept, statement_history, last_analyze, *alive_players* (not for speak)

                Output format:
                {
                    "identity": "",
                    "strategy": "",
                    "statement": ""
                }
                =====================================================
                """

                ret = call_api(llm_info)
                ret_json, error = safe_parse_json(ret)
                if error:
                    print(f"JSON parsing error: {error}")
                self.last_analyze = ret_json.get('identity', '')
                return ret_json.get('statement', '')
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise e
    
    def vote(self, statement_history, active_players: List['Player']) -> Tuple[int, str]:
        """
        Call LLM API to make voting decisions
        
        Parameters:
            statement_history: All statements in this game
            active_players: List of active players
            
        Returns:
            Tuple[int, str]: Voted player ID and reasoning
        """
        # Use round history for context in voting decision
        #  statement_history = game_state.get("statement_history", {})
        
        # Build prompt with history context
        # prompt = _build_voting_prompt(game_state, active_players, statement_history)

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                llm_info = {
                    "model": self.llm_id,
                    "temperature": llm_set["temperature"],
                    "max_tokens": llm_set["max_tokens"],
                    "input_messages": [
                        {"role": "system", "content": self.prompt.system_vote_player()},
                        {"role": "user", "content": self.prompt.user_vote_player(self.player_id, self.assigned_concept, statement_history, self.last_analyze, active_players)}
                    ]
                }

                """
                ======================= PROMPT =======================
                User input (5 neccesary): 
                player_id, assigned_concept, statement_history, last_analyze, alive_players

                Output format:
                {
                    "identity": "",
                    "strategy": "",
                    "vote": ""
                }
                =====================================================
                """


                ret = call_api(llm_info)
                ret_json, error = safe_parse_json(ret)
                if error:
                    print(f"JSON parsing error: {error}")
                vot = ret_json.get('vote', '')
                
                vot = str(vot)
                if vot.startswith("Player_") or vot.startswith("player_"):
                    vot = vot.replace("Player_", "").replace("player_", "")
                try:
                    vot = int(vot)
                except ValueError:
                    pass
                return vot
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise e


