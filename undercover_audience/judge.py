from abc import ABC, abstractmethod
from typing import Dict, Any

class Judge(ABC):
    """
    Abstract base class for game judge, responsible for evaluating player descriptions
    and checking rule violations
    """
    def __init__(self, judge_id: str, judge_version: str, language: str):
        self.judge_id = judge_id
        self.judge_version = judge_version
        self.language = language
    @abstractmethod
    def evaluate_statement(self, statement: str, player_concept: str, 
                         statement_round: int) -> Dict[str, Any]:
        """
        Evaluate a player's statement and calculate metrics
        
        Parameters:
            statement: The player's statement
            player_concept: The concept assigned to the player
            statement_round: The current statement round
            
        Returns:
            Dict with evaluation metrics
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert judge information to a dictionary for JSON serialization"""
        return {
            "id": self.judge_id,
            "version": self.judge_version
        }
    
    def evaluate_game_result(self, game_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the overall game and provide insights
        This method is optional for judges to implement
        
        Parameters:
            game_record: Complete game record data
            
        Returns:
            Dict with game analysis
        """
        # Default implementation that can be overridden by subclasses
        return self._default_game_analysis(game_record)
    