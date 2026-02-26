from typing import List, Dict, Any
from undercover.player import Player
from undercover.interface.game_interface import GameInterface

class HumanPlayer(Player):
    """
    Human player implementation for the Undercover game
    Handles user input through command line interface
    """

    def __init__(self, player_id: int, language: str):
        """
        Initialize the human player

        Parameters:
            player_id: Unique identifier for the player
            language: Game language (en, zh, etc.)
        """
        super().__init__(player_id, "human", language)
        self.interface = GameInterface()
        self.current_round_number = 0
        self.current_statement_round = 0
        self.concept_familiarity = None  # Will store human's familiarity with the concept

    def set_game_start_info(self, total_players: int):
        """
        Display initial game information when the game starts
        Called after role assignment is complete

        Parameters:
            total_players: Total number of players in the game
        """
        self.interface.display_game_start(
            player_id=self.player_id,
            concept=self.assigned_concept,
            total_players=total_players
        )

        # Ask human player about their familiarity with the concept
        self.concept_familiarity = self.interface.get_concept_familiarity(
            player_id=self.player_id,
            concept=self.assigned_concept
        )

    def generate_statement(self, statement_history: str) -> str:
        """
        Get a statement input from the human player

        Parameters:
            statement_history: String containing all previous statements

        Returns:
            str: The human player's statement
        """
        return self.interface.get_statement_input(
            player_id=self.player_id,
            concept=self.assigned_concept,
            statement_history=statement_history
        )

    def vote(self, statement_history: str, active_players: List['Player']) -> int:
        """
        Get voting input from the human player

        Parameters:
            statement_history: String containing all previous statements
            active_players: List of players still in the game

        Returns:
            int: The ID of the player being voted for
        """
        return self.interface.get_vote_input(
            player_id=self.player_id,
            concept=self.assigned_concept,
            statement_history=statement_history,
            active_players=active_players
        )

    def display_round_start(self, round_number: int, statement_round: int, statement_history: str):
        """
        Display information at the start of a statement round

        Parameters:
            round_number: Current voting round
            statement_round: Current statement round
            statement_history: String containing all previous statements
        """
        self.current_round_number = round_number
        self.current_statement_round = statement_round
        self.interface.display_round_start(round_number, statement_round)
        self.interface.display_statement_history(statement_history, self.player_id)

    def display_voting_round(self, voting_round: int, active_players: List[Player]):
        """
        Display voting round information

        Parameters:
            voting_round: Current voting round number
            active_players: List of players still in the game
        """
        self.interface.display_voting_round(voting_round, active_players)

    def display_elimination_result(self, eliminated_player: Player, was_correct: bool, voter_count: int):
        """
        Display the result of voting elimination

        Parameters:
            eliminated_player: The player who was eliminated
            was_correct: Whether the elimination was correct
            voter_count: Number of votes received
        """
        self.interface.display_elimination_result(eliminated_player, was_correct, voter_count)

    def display_metric_elimination(self, player: Player, reason: str):
        """
        Display metric-based elimination information

        Parameters:
            player: The eliminated player
            reason: Reason for elimination
        """
        self.interface.display_metric_elimination(player, reason)

    def display_game_over(self, winner_role: str, all_players: List[Player]):
        """
        Display final game results

        Parameters:
            winner_role: The winning role
            all_players: All players in the game
        """
        self.interface.display_game_over(winner_role, self, all_players)

    def display_error(self, message: str):
        """
        Display an error message

        Parameters:
            message: Error message to display
        """
        self.interface.display_error(message)