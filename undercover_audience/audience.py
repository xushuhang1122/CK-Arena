from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

class Audience(ABC):
    """
    Abstract base class for an audience in the game
    Specific audience implementations will inherit this class and implement the relevant methods
    """
    def __init__(self, audience_id: str, llm_id: str, language: str):
        self.audience_id = audience_id
        self.llm_id = llm_id
        self.language = language
        self.last_analyze = ""
        
    @abstractmethod
    def choose_player_to_eliminate(self, statement_history, active_players) -> Tuple[int, str]:
        """
        Choose which player to eliminate based on statements
        
        Parameters:
            statement_history: History of all statements
            active_players: List of players still in the game
            
        Returns:
            Tuple[int, str]: ID of the player to eliminate and elimination reason
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audience information to a dictionary for JSON serialization"""
        return {
            "audience_id": self.audience_id,
            "llm_id": self.llm_id,
            "language": self.language
        }