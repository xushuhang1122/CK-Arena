import random
import json
from typing import List, Dict, Any, Optional, Tuple

from undercover_audience.player import Player
from undercover_audience.agents.utils import call_api, llm_set
from undercover_audience.agents.json_validator import safe_parse_json

class LLMPlayerAU(Player):
    """
    LLM-based player implementation
    Uses an LLM to generate statements and voting decisions
    """
    def __init__(self, player_id: int, llm_id: str, language: str):
        super().__init__(player_id, llm_id, language)
        if language == "zh":
            from undercover_audience.agents.prompts import player_prompt_zh
            self.prompt = player_prompt_zh
        elif language == "en":
            from undercover_audience.agents.prompts import player_prompt_en
            self.prompt = player_prompt_en
        elif language == "fr":
            from undercover_audience.agents.prompts import player_prompt_fr
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
                        {"role": "user", "content": self.prompt.user_speak_player(self.player_id, self.assigned_concept,self.another_concept, self.role, statement_history, "")}
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
