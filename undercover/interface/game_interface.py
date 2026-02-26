import os
import sys
from typing import List, Dict, Any, Optional
from undercover.player import Player

class GameInterface:
    """
    Command line interface for human player interaction in the Undercover game
    Handles game state display, user input collection, and user experience
    """

    def __init__(self):
        self.clear_screen()

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Print a formatted header"""
        print("=" * 60)
        print(f" {title} ".center(60, "="))
        print("=" * 60)

    def print_separator(self):
        """Print a separator line"""
        print("-" * 60)

    def display_game_start(self, player_id: int, concept: str, total_players: int):
        """
        Display initial game information for the human player

        Parameters:
            player_id: The human player's ID number
            concept: The player's assigned concept
            total_players: Total number of players in the game
        """
        self.clear_screen()
        self.print_header("UNDERCOVER GAME STARTED")

        print(f"\nWelcome to Undercover!")
        print(f"You are Player {player_id} out of {total_players} players")
        print(f"Your concept: {concept}")

        print("\n" + "="*50)
        print("IMPORTANT: You don't know your role!")
        print("You could be either a CIVILIAN or an UNDERCOVER.")
        print("Your task is to:")
        print("- Describe your concept appropriately based on what you think your role is")
        print("- Listen to other players' descriptions carefully")
        print("- Vote for who you think are the undercover players")
        print("- Remember: Undercovers might not know they're undercovers!")
        print("="*50)

        print("\nPress Enter to start the game...")
        input()

    def display_round_start(self, round_number: int, statement_round: int):
        """
        Display information at the start of a round

        Parameters:
            round_number: Current voting round
            statement_round: Current statement round
        """
        self.clear_screen()
        self.print_header(f"ROUND {round_number} - STATEMENT {statement_round}")
        print()

    def display_statement_history(self, statement_history: str, current_player_id: int):
        """
        Display the history of statements from previous rounds

        Parameters:
            statement_history: String containing all previous statements
            current_player_id: ID of the human player
        """
        if not statement_history.strip():
            print("No previous statements yet.")
            return

        print("Previous Statements:")
        self.print_separator()

        lines = statement_history.strip().split('\n')
        for line in lines:
            if line.strip():
                # Highlight human player's own statements
                if f"Player_{current_player_id}:" in line:
                    print(f">>> {line} <<< (YOUR STATEMENT)")
                else:
                    print(line)
        print()

    def get_statement_input(self, player_id: int, concept: str, statement_history: str) -> str:
        """
        Get a statement input from the human player

        Parameters:
            player_id: The player's ID
            concept: The player's assigned concept
            statement_history: History of all previous statements

        Returns:
            str: The player's statement
        """
        self.print_separator()
        print(f"Your turn to speak! (Player {player_id})")
        print(f"Your concept: {concept}")
        print(f"\nDescribe your concept in one sentence.")
        print("Be creative but clear - too vague or too obvious may get you eliminated!")

        while True:
            print("\nYour statement:")
            statement = input("> ").strip()

            if not statement:
                print("Error: Statement cannot be empty. Please try again.")
                continue

            if concept.lower() in statement.lower():
                print("Error: Your statement contains your concept word!")
                print("This would immediately reveal your role. Please try again.")
                continue

            # Basic length validation
            if len(statement) < 5:
                print("Error: Statement too short. Please provide a more descriptive statement.")
                continue

            if len(statement) > 200:
                print("Error: Statement too long. Please keep it under 200 characters.")
                continue

            # Confirmation
            print(f"\nYour statement: \"{statement}\"")
            confirm = input("Submit this statement? (y/n): ").lower().strip()
            if confirm == 'y':
                return statement
            elif confirm == 'n':
                continue
            else:
                print("Please enter 'y' to confirm or 'n' to try again.")

    def display_voting_round(self, voting_round: int, active_players: List[Player]):
        """
        Display information for the voting round

        Parameters:
            voting_round: Current voting round number
            active_players: List of players still in the game
        """
        self.clear_screen()
        self.print_header(f"VOTING ROUND {voting_round}")
        print("\nTime to vote! Choose who you think is the undercover.")
        print("Active players:")
        self.print_separator()

        for player in active_players:
            status = "(YOU)" if player.llm_id == "human" else f"({player.llm_id})"
            print(f"Player {player.player_id}: {status}")
        print()

    def get_vote_input(self, player_id: int, concept: str, statement_history: str, active_players: List[Player]) -> int:
        """
        Get voting input from the human player

        Parameters:
            player_id: The voting player's ID
            concept: The player's assigned concept
            statement_history: History of all statements
            active_players: List of players eligible for voting

        Returns:
            int: The ID of the player being voted for
        """
        print(f"\nYour turn to vote! (Player {player_id})")
        print(f"Your concept: {concept}")

        # Show recent statements for reference
        self.display_statement_history(statement_history, player_id)

        active_player_ids = [p.player_id for p in active_players]

        while True:
            print(f"\nWho do you think is the undercover?")
            print("Available options:", ", ".join(map(str, active_player_ids)))

            try:
                vote_input = input(f"Vote for player (enter number {active_player_ids[0]}-{active_player_ids[-1]}): ").strip()
                voted_id = int(vote_input)

                if voted_id not in active_player_ids:
                    print(f"Error: Player {voted_id} is not active. Please choose from available players.")
                    continue

                if voted_id == player_id:
                    print("Error: You cannot vote for yourself!")
                    continue

                # Get voting reason
                reason = input("Brief reason for your vote (optional): ").strip()

                # Confirmation
                voted_player = next(p for p in active_players if p.player_id == voted_id)
                llm_info = " (YOU)" if voted_player.llm_id == "human" else f" ({voted_player.llm_id})"

                print(f"\nYou are voting for Player {voted_id}{llm_info}")
                if reason:
                    print(f"Reason: {reason}")

                confirm = input("Confirm this vote? (y/n): ").lower().strip()
                if confirm == 'y':
                    print(f"Vote submitted: Player {voted_id}")
                    return voted_id
                elif confirm == 'n':
                    continue
                else:
                    print("Please enter 'y' to confirm or 'n' to change your vote.")

            except ValueError:
                print("Error: Please enter a valid player number.")

    def display_elimination_result(self, eliminated_player: Player, was_correct: bool, voter_count: int):
        """
        Display the result of the voting elimination

        Parameters:
            eliminated_player: The player who was eliminated
            was_correct: Whether the elimination was correct (undercover eliminated)
            voter_count: Number of votes for the eliminated player
        """
        self.print_separator()
        print(f"VOTING RESULT:")
        print(f"Player {eliminated_player.player_id} ({eliminated_player.llm_id}) was eliminated!")
        print(f"Role: {eliminated_player.role.upper()}")
        print(f"Votes received: {voter_count}")

        if was_correct:
            print("✓ CORRECT! An undercover player was eliminated.")
        else:
            print("✗ INCORRECT! A civilian was eliminated.")

        print("\nPress Enter to continue...")
        input()

    def display_metric_elimination(self, player: Player, reason: str):
        """
        Display information when a player is eliminated due to low scores

        Parameters:
            player: The eliminated player
            reason: The reason for elimination (low scores)
        """
        self.print_separator()
        print(f"METRIC ELIMINATION:")
        print(f"Player {player.player_id} ({player.llm_id}) was eliminated by the judges!")
        print(f"Reason: {reason}")

        if player.llm_id == "human":
            print("⚠️  Your statement scored too low on novelty or reasonableness.")
            print("Try to be more creative and reasonable in your statements.")

        print("\nPress Enter to continue...")
        input()

    def display_game_over(self, winner_role: str, human_player: Player, all_players: List[Player]):
        """
        Display the final game results

        Parameters:
            winner_role: The winning role (civilian or undercover)
            human_player: The human player object
            all_players: All players in the game
        """
        self.clear_screen()
        self.print_header("GAME OVER")

        print(f"\n🏆 WINNER: {winner_role.upper()}S! 🏆")

        print(f"\nYour final result:")
        if human_player.is_winner:
            print("✓ CONGRATULATIONS! You won!")
        else:
            print("✗ You were eliminated. Better luck next time!")

        print(f"\nFinal player status:")
        self.print_separator()
        for player in all_players:
            status = "WINNER" if player.is_winner else "ELIMINATED"
            marker = " (YOU)" if player.llm_id == "human" else ""
            print(f"Player {player.player_id} ({player.llm_id}): {player.role.upper()} - {status}{marker}")

        print("\nThanks for playing Undercover!")
        print("\nPress Enter to exit...")
        input()

    def display_error(self, message: str):
        """
        Display an error message

        Parameters:
            message: The error message to display
        """
        print(f"\n❌ ERROR: {message}")
        print("Press Enter to continue...")
        input()

    def get_concept_familiarity(self, player_id: int, concept: str) -> Dict[str, Any]:
        """
        Ask the human player about their familiarity with the assigned concept

        Parameters:
            player_id: The human player's ID number
            concept: The player's assigned concept

        Returns:
            Dict[str, Any]: Dictionary containing familiarity information
        """
        print(f"\n" + "="*60)
        print(" CONCEPT FAMILIARITY SURVEY ".center(60, "="))
        print("="*60)

        print(f"\nYour assigned concept is: {concept}")
        print("Please rate your familiarity with this concept to help improve the game:")
        print()

        familiarity_scale = {
            1: "1 - Never heard of it before",
            2: "2 - Heard of it but don't know much",
            3: "3 - Somewhat familiar",
            4: "4 - Quite familiar",
            5: "5 - Very familiar"
        }

        for rating, description in familiarity_scale.items():
            print(f"  {description}")

        print("\nAdditional context (optional):")
        print("  - How you first learned about this concept")
        print("  - Any personal experience with it")
        print("  - Your confidence in describing it")

        while True:
            try:
                familiarity_input = input(f"\nYour familiarity rating (1-5): ").strip()
                familiarity = int(familiarity_input)
                if 1 <= familiarity <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 5.")

        context_input = input("Additional context (optional, press Enter to skip): ").strip()

        print(f"\nThank you! Your familiarity with '{concept}' has been recorded.")
        print("This information will help improve the game balance.")
        print("="*60)
        print("\nPress Enter to start the game...")
        input()

        return {
            "familiarity_rating": familiarity,
            "context": context_input if context_input else None,
            "concept": concept
        }