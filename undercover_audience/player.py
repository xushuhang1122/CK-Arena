from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

class Player(ABC):
    """
    Abstract base class for a player in the game
    Specific player implementations will inherit this class and implement the relevant methods
    """
    def __init__(self, player_id: int, llm_id: str, language: str):
        self.player_id = player_id
        self.llm_id = llm_id
        self.last_analyze = ""
        self.role = None  # 'civilian' or 'undercover'
        self.assigned_concept = None  # The assigned word/concept
        self.another_concept = None
        self.eliminated = False
        self.eliminated_in_voting_round = None
        self.is_winner = False
        self.language = language
    def assign_role(self, role: str, concept: str, another_concept: str):
        """Assign a role and corresponding concept to the player"""
        self.role = role
        self.assigned_concept = concept
        self.another_concept = another_concept
    def eliminate(self, voting_round: int):
        """Mark the player as eliminated"""
        self.eliminated = True
        self.eliminated_in_voting_round = voting_round

        
    def set_as_winner(self):
        """Mark the player as a winner"""
        self.is_winner = True
        
    @abstractmethod
    def generate_statement(self, game_state: Dict[str, Any]) -> str:
        """
        Generate a statement describing the player's assigned concept
        Parameters:
            game_state: Current game state
            statement_round: Current statement round
        Returns:
            str: Player's statement content
        """
        pass
        


    def to_dict(self) -> Dict[str, Any]:
        """Convert player information to a dictionary for JSON serialization"""
        return {
            "player_id": self.player_id,
            "llm_id": self.llm_id,
            "role": self.role,
            "assigned_concept": self.assigned_concept,
            "eliminated_in_voting_round": self.eliminated_in_voting_round,
            "is_winner": self.is_winner
        }


    