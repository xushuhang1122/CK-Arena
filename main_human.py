import json
import os
import datetime
import random
from undercover.game_human import UndercoverHumanGame
from undercover.agents.player_agent import LLMPlayer
from undercover.agents.judge_agent import LLMJudge
from undercover.agents.human_player import HumanPlayer

def create_human_game(llm_players_count=5, language="en"):
    """
    Create a game with 1 human player and specified number of LLM players

    Parameters:
        llm_players_count: Number of LLM players to create (default: 5)
        language: Game language (default: "en")

    Returns:
        tuple: (players, judges) lists ready for game creation
    """
    # Create the human player
    players = [HumanPlayer(player_id=1, language=language)]

    # Create LLM players with IDs starting from 2
    available_llms = [
        "gpt-4o",
        "qwen2.5-72b",
        "deepseek-v3",
        "kimi-k2-instruct",
        "deepseek-v3.1"
    ]

    # Randomly select LLMs for diversity
    selected_llms = random.sample(available_llms, min(llm_players_count, len(available_llms)))

    for i, llm_id in enumerate(selected_llms):
        player_id = i + 2  # Start from ID 2 since human is ID 1
        players.append(LLMPlayer(player_id, llm_id, language))

    # Create judges (can use existing judge configurations)
    judges = [
        LLMJudge("judge-1", "claude-3-7-sonnet-20250219", language),
        LLMJudge("judge-2", "gpt-4-0125-preview", language)
    ]

    return players, judges

def shuffle_player_positions(players):
    """
    Randomly shuffle player positions while keeping track of human player

    Parameters:
        players: List of player objects

    Returns:
        tuple: (shuffled_players, human_player_new_id)
    """
    # Find the human player
    human_player = None
    human_original_id = None

    for i, player in enumerate(players):
        if isinstance(player, HumanPlayer):
            human_player = player
            human_original_id = i + 1  # Player IDs are 1-based
            break

    if human_player is None:
        return players, None

    # Create a copy of players and shuffle their positions
    shuffled_indices = list(range(len(players)))
    random.shuffle(shuffled_indices)

    shuffled_players = [None] * len(players)
    human_new_id = None

    for old_pos, new_pos in enumerate(shuffled_indices):
        shuffled_players[new_pos] = players[old_pos]

        # Update player IDs to match new positions
        shuffled_players[new_pos].player_id = new_pos + 1

        # Track human player's new position
        if isinstance(players[old_pos], HumanPlayer):
            human_new_id = new_pos + 1

    return shuffled_players, human_new_id

def run_human_game(game_settings):
    """
    Run a game with 1 human player and 5 LLM players

    Parameters:
        game_settings: Game configuration dictionary

    Returns:
        dict: Game record
    """
    # Create players (1 human + 5 LLM)
    players, judges = create_human_game(
        llm_players_count=5,
        language=game_settings["language"]
    )

    # Randomly shuffle player positions
    shuffled_players, human_new_id = shuffle_player_positions(players)

    print(f"Human player assigned to position: {human_new_id}")

    # Game parameters
    game_params = {
        "judges": judges,
        "players": shuffled_players,
        "topic_category": game_settings["topic_category"],
        "concept_pair": (game_settings["pair"][0], game_settings["pair"][1]),
        "civilian_count": game_settings["civilian_count"],
        "undercover_count": game_settings["undercover_count"],
        "max_statement_rounds": game_settings["max_statement_rounds"],
        "statements_per_voting": game_settings["statements_per_voting"]
    }

    # Create and run game
    game = UndercoverHumanGame(**game_params)
    game.run_game()

    # Save game record
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create directory structure for human games
    human_log_dir = os.path.join(logs_dir, "human_games_familiar")
    if not os.path.exists(human_log_dir):
        os.makedirs(human_log_dir)

    language_dir = os.path.join(human_log_dir, game_settings["language"])
    if not os.path.exists(language_dir):
        os.makedirs(language_dir)

    topic_dir = os.path.join(language_dir, game_settings["topic_category"])
    if not os.path.exists(topic_dir):
        os.makedirs(topic_dir)

    # Construct the file path
    filename = f"{game_settings['pair'][0]}_{game_settings['pair'][1]}_{timestamp}.json"
    file_path = os.path.join(topic_dir, filename)

    # Save game record
    game.save_game_record(file_path)

    return game.get_game_record()

def print_game_summary(game_record):
    """
    Print a summary of the human game result

    Parameters:
        game_record: The game record dictionary
    """
    record = game_record["game_record"]

    print("\n" + "="*50)
    print(f"Human Game ID: {record['game_id']}")
    print(f"Topic: {record['topic_category']}")
    print(f"Concepts: {record['concept_pair']['concept_a']} vs {record['concept_pair']['concept_b']}")
    print("="*50)

    # Find human player
    human_player = None
    for player in record["players"]:
        if player["llm_id"] == "human":
            human_player = player
            break

    if human_player:
        print(f"Human Player (ID {human_player['player_id']}):")
        print(f"  Role: {human_player['role'].upper()}")
        print(f"  Result: {'WINNER' if human_player['is_winner'] else 'LOST'}")

    summary = record["game_summary"]
    print(f"\nGame Summary:")
    print(f"  Winner: {summary['winner_role'].upper()}")
    print(f"  Total rounds: {summary['total_statement_rounds']}")
    print(f"  Total statements: {summary['total_statements']}")
    print(f"  Correct identifications: {summary['correct_identifications']}")
    print(f"  Incorrect identifications: {summary['incorrect_identifications']}")

    print("="*50 + "\n")

def display_welcome():
    """Display welcome message for automated game"""
    print("="*70)
    print(" UNDERCOVER - AUTOMATED EVALUATION EDITION ".center(70, "="))
    print("="*70)
    print("\nStarting automated Undercover game with 1 human + 5 AI players")
    print("Using automated evaluation instead of LLM judges")
    print("="*70 + "\n")

if __name__ == "__main__":
    display_welcome()

    # Load word pairs
    data_path = ""
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            word_pairs = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find word data file at {data_path}")
        print("Using default word pairs...")
        word_pairs = [["shirt", "jacket"], ["hat", "cap"], ["pants", "trousers"]]

    # Select random word pair
    selected_pair = random.choice(word_pairs)

    game_settings = {
        "log_folder_path": "human_games_familiar",
        "topic_category": "foods",
        "pair": ["whale", "shark"],
        "civilian_count": 4,
        "undercover_count": 2,
        "max_statement_rounds": 5,
        "statements_per_voting": 1,
        "language": "en"
    }

    print(f"Game Configuration:")
    print(f"  Topic: {game_settings['topic_category']}")
    print(f"  Players: 1 Human + 5 AI")
    print(f"  Max rounds: {game_settings['max_statement_rounds']}")
    print(f"  Language: {game_settings['language']}")
    print(f"  Evaluation: Automated (reasonableness + novelty)")
    print()

    print("Starting automated game...")

    try:
        game_record = run_human_game(game_settings)
        print_game_summary(game_record)

        # Optional: Print the full game record in JSON format
        print("Full game record saved to logs/human_games_familiar/")
        # print(json.dumps(game_record, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nError during game: {e}")
        print("Please check the game configuration and try again.")