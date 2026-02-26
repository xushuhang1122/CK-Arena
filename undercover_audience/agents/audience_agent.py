import random
import json
from typing import List, Dict, Any, Optional, Tuple

from undercover_audience.audience import Audience
from undercover_audience.agents.utils import call_api, llm_set
from undercover_audience.agents.json_validator import safe_parse_json

class LLMAudience(Audience):
    """
    LLM-based audience implementation
    Uses an LLM to analyze player statements and choose who to eliminate
    """
    def __init__(self, audience_id: str, llm_id: str, language: str):
        super().__init__(audience_id, llm_id, language)
        if language == "zh":
            from undercover_audience.agents.prompts import audience_prompt_zh
            self.prompt = audience_prompt_zh
        elif language == "en":
            from undercover_audience.agents.prompts import audience_prompt_en
            self.prompt = audience_prompt_en
        elif language == "fr":
            from undercover_audience.agents.prompts import audience_prompt_fr
            self.prompt = audience_prompt_fr
    
    def choose_player_to_eliminate(self, statement_history: str, active_players: List['Player']) -> Tuple[int, str]:
        """
        Call LLM API to analyze statements and choose a player to eliminate
        
        Parameters:
            statement_history: All statements made in the game
            active_players: List of active players
            
        Returns:
            Tuple[int, str]: ID of player to eliminate and reasoning
        """
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                llm_info = {
                    "model": self.llm_id,
                    "temperature": llm_set["temperature"],
                    "max_tokens": llm_set["max_tokens"],
                    "input_messages": [
                        {"role": "system", "content": self.prompt.system_audience()},
                        {"role": "user", "content": self.prompt.user_audience(statement_history, active_players)}
                    ]
                }

                """
                ======================= PROMPT =======================
                User input (3 necessary): 
                statement_history, last_analyze, active_players

                Output format:
                {
                    "analysis": "",
                    "eliminate": ""
                }
                =====================================================
                """

                ret = call_api(llm_info)
                ret_json, error = safe_parse_json(ret)
                if error:
                    print(f"JSON parsing error: {error}")
                    ret_json = {}
                
                # Update last analysis for next round
                reasoning = ret_json.get('analysis', '')
                eliminate = ret_json.get('eliminate', '')
                
                # Parse player ID from response
                eliminate = str(eliminate)
                if eliminate.startswith("Player_") or eliminate.startswith("player_"):
                    eliminate = eliminate.replace("Player_", "").replace("player_", "")
                try:
                    eliminate_id = int(eliminate)
                except ValueError:
                    # If parsing fails, randomly choose a player
                    eliminate_id = random.choice([p.player_id for p in active_players])
                    reasoning = "Failed to parse LLM response, choosing randomly"
                
                return eliminate_id, reasoning
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    # If all retries fail, choose randomly
                    random_player = random.choice(active_players)
                    return random_player.player_id, f"API call failed after {max_retries} attempts: {str(e)}"