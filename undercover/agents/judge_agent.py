import random
import json
from typing import Dict, Any, List, Optional

from undercover.judge import Judge
from undercover.agents.utils import call_api, llm_set
from undercover.agents.json_validator import safe_parse_json

class LLMJudge(Judge):
    """
    LLM-based implementation of game judge
    Uses an LLM to evaluate player statements and calculate metrics
    """
    def __init__(self, judge_id: str, judge_version: str, language: str):
        super().__init__(judge_id, judge_version, language)
        if language == "zh":
            from undercover.agents.prompts import judge_prompt_zh
            self.prompt = judge_prompt_zh
        elif language == "en":
            from undercover.agents.prompts import judge_prompt_en
            self.prompt = judge_prompt_en
        elif language == "fr":
            from undercover.agents.prompts import judge_prompt_fr
            self.prompt = judge_prompt_fr
    def evaluate_statement(self, statement_history, statement, word1, word2):
        """
        Evaluate a player's statement using an LLM

        Parameters:
            statement_history: All statements in this game
            statement: The player's statement
            word 1/2: The two words in this game (1 = civilian and 2 = undercover)
            
        Returns:
            Dict with evaluation metrics
        """
        # Build prompt for evaluation
        # round_history = game_state.get("round_history", {})

        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                llm_info = {
                    "model": self.judge_id,
                    "temperature": llm_set["temperature"],
                    "max_tokens": llm_set["max_tokens"],
                    "input_messages": [
                        {"role": "system", "content": self.prompt.system_judge()},
                        {"role": "user", "content": self.prompt.user_judge(word1, word2, statement, statement_history)}
                    ]
                }

                """
                Output format:

                {
                    "novelty": {
                    "score": (0, 0.2, 0.4, 0.6, 0.8, 1),
                    "explanation": ""
                    },
                    "relevance": {
                    "score": (0, 0.2, 0.4, 0.6, 0.8, 1),
                    "explanation": ""
                    },
                    "reasonableness": {
                    "score": (0, 0.2, 0.4, 0.6, 0.8, 1),
                    "explanation": ""
                    }
                }
                
                """

                ret = call_api(llm_info)
                ret_json, error = safe_parse_json(ret)
                if error:
                    print(f"JSON parsing error: {error}")
                novelty_score = ret_json["novelty"]["score"]
                relevance_score = ret_json["relevance"]["score"]
                reasonableness_score = ret_json["reasonableness"]["score"]

                return novelty_score, relevance_score, reasonableness_score
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    print(f"\nWrong judge response:\n{ret}\n")
                    raise e
