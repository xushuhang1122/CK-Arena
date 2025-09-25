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
    
    def generate_statement(self, statement_history) -> Dict[str, Any]:
        """
        Call LLM API to generate a description
        
        Parameters:
            statement_history: All statements in this game
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - content: The final statement
                - full_response: Complete LLM response
                - thinking_process: Extracted thinking process
                - llm_info: Information about the LLM call
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

                full_llm_response = call_api(llm_info)
                
                ret_json, error = safe_parse_json(full_llm_response)
                if error:
                    print(f"JSON parsing error: {error}")
                
                self.last_analyze = ret_json.get('identity', '')
                
                statement_content = ret_json.get('statement', '')
                

                thinking_process = self._extract_thinking_process(ret_json, full_llm_response)

                return {
                    'content': statement_content,
                    'full_response': full_llm_response,
                    'thinking_process': thinking_process,
                    'llm_info': llm_info,
                    'parsed_json': ret_json
                }
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    return {
                        'content': f"Error generating statement: {str(e)}",
                        'full_response': f"Error occurred: {str(e)}",
                        'thinking_process': f"Error in statement generation: {str(e)}",
                        'llm_info': llm_info if 'llm_info' in locals() else {},
                        'parsed_json': {}
                    }
    
    def vote(self, statement_history, active_players: List['Player']) -> Dict[str, Any]:
        """
        Call LLM API to make voting decisions
        
        Parameters:
            statement_history: All statements in this game
            active_players: List of active players
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - voted_id: The player ID voted for
                - full_response: Complete LLM response
                - thinking_process: Extracted thinking process
                - llm_info: Information about the LLM call
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


                full_llm_response = call_api(llm_info)
                

                ret_json, error = safe_parse_json(full_llm_response)
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
                
                thinking_process = self._extract_thinking_process(ret_json, full_llm_response)
                
                return {
                    'voted_id': vot,
                    'full_response': full_llm_response,
                    'thinking_process': thinking_process,
                    'llm_info': llm_info,
                    'parsed_json': ret_json
                }
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    return {
                        'voted_id': None,
                        'full_response': f"Error occurred: {str(e)}",
                        'thinking_process': f"Error in voting: {str(e)}",
                        'llm_info': llm_info if 'llm_info' in locals() else {},
                        'parsed_json': {}
                    }
    
    def _extract_thinking_process(self, ret_json: Dict, full_response: str) -> str:

        thinking_parts = []
        

        if ret_json:
            identity = ret_json.get('identity', '')
            strategy = ret_json.get('strategy', '')
            
            if identity:
                thinking_parts.append(f"Identity Analysis: {identity}")
            if strategy:
                thinking_parts.append(f"Strategy: {strategy}")
        

        if '<thinking>' in full_response and '</thinking>' in full_response:
            start = full_response.find('<thinking>') + len('<thinking>')
            end = full_response.find('</thinking>')
            thinking_content = full_response[start:end].strip()
            if thinking_content:
                thinking_parts.append(f"Raw Thinking: {thinking_content}")
        

        if thinking_parts:
            return "\n".join(thinking_parts)
        else:
            return full_response
    

    def generate_statement_legacy(self, statement_history) -> str:

        result = self.generate_statement(statement_history)
        return result.get('content', '') if isinstance(result, dict) else str(result)
    
    def vote_legacy(self, statement_history, active_players: List['Player']) -> int:

        result = self.vote(statement_history, active_players)
        return result.get('voted_id') if isinstance(result, dict) else result