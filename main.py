import json
import os
import datetime
from undercover.game import UndercoverGame
from undercover_audience.game import UndercoverAudienceGame
from undercover.agents.player_agent import LLMPlayer
from undercover.agents.judge_agent import LLMJudge
from undercover_audience.agents.audience_agent import LLMAudience
from undercover_audience.agents.player_agent import LLMPlayerAU
from undercover_audience.agents.judge_agent import LLMJudgeAU

def run_game(players, judges, game_settings, game_mode="standard", audience_llm=None):
    """
    Run a game with specified settings
    
    Parameters:
        players: List of player configurations
        judges: List of judge configurations  
        game_settings: Game configuration dictionary
        game_mode: "standard" for player voting, "audience" for audience decision
        audience_llm: LLM configuration for audience mode [model, provider]
    """
    judge_list = []
    player_list = []
    
    # Use appropriate classes based on game mode
    if game_mode == "audience":
        JudgeClass = LLMJudgeAU
        PlayerClass = LLMPlayerAU
    else:
        JudgeClass = LLMJudge
        PlayerClass = LLMPlayer
    
    # Create judges
    for judge in judges:
        judge_list.append(JudgeClass(judge[0], judge[1], game_settings["language"]))
    
    # Create players
    for i, player in enumerate(players):
        player_list.append(PlayerClass(i + 1, player[0], game_settings["language"]))
    
    game_params = {
        "judges": judge_list,
        "players": player_list,
        "topic_category": game_settings["topic_category"],
        "concept_pair": (game_settings["pair"][0], game_settings["pair"][1]),
        "civilian_count": game_settings["civilian_count"],
        "undercover_count": game_settings["undercover_count"],
        "max_statement_rounds": game_settings["max_statement_rounds"],
        "statements_per_voting": game_settings["statements_per_voting"]
    }
    
    if game_mode == "audience":
        # Create audience for audience mode
        if audience_llm is None:
            audience_llm = ["claude-3-7-sonnet-20250219", ""]
        audience = LLMAudience("audience-1", audience_llm[0], game_settings["language"])
        game = UndercoverAudienceGame(
            **game_params,
            audience=audience
        )
    else:
        # Standard game mode
        game = UndercoverGame(**game_params)
    
    # Run game
    game.run_game()
    
    # Save game record
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    # Add game mode to folder path
    tag_dir = os.path.join(logs_dir, f"{game_settings['log_folder_path']}_{game_mode}")
    if not os.path.exists(tag_dir):
        os.makedirs(tag_dir)
        
    language_dir = os.path.join(tag_dir, game_settings["language"])
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

def print_game_summary(game_record, game_mode="standard"):
    """
    Print a summary of the game result
    
    Parameters:
        game_record: The game record dictionary
        game_mode: "standard" or "audience" to indicate game type
    """
    record = game_record["game_record"]
    
    print("\n" + "="*50)
    print(f"Game ID: {record['game_id']}")
    print(f"Game Mode: {game_mode.upper()}")
    print(f"Topic: {record['topic_category']}")
    print(f"Concepts: {record['concept_pair']['concept_a']} vs {record['concept_pair']['concept_b']}")
    print("="*50)
    
    # Print players
    print("\nPlayers:")
    for player in record["players"]:
        status = "WINNER" if player["is_winner"] else "ELIMINATED" if player["eliminated_in_voting_round"] else "ACTIVE"
        print(f"  Player {player['player_id']} ({player['llm_id']}): {player['role'].upper()} - {status}")
    
    # Print judges
    print("\nJudges:")
    for judge in record["judges"]:
        print(f"  Judge: {judge['id']} ({judge['version']})")
    
    # Print audience if in audience mode
    if game_mode == "audience" and "audience" in record:
        print("\nAudience:")
        print(f"  Audience: {record['audience']['audience_id']} ({record['audience']['llm_id']})")
    
    # Print game summary
    summary = record["game_summary"]
    print("\nGame Summary:")
    print(f"  Winner: {summary['winner_role'].upper()}")
    print(f"  Total rounds: {summary['total_statement_rounds']}")
    print(f"  Total statements: {summary['total_statements']}")
    print(f"  Decision quality: {summary['game_decision_quality']:.2f}")
    print(f"  Correct identifications: {summary['correct_identifications']}")
    print(f"  Incorrect identifications: {summary['incorrect_identifications']}")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    # Game mode selection
    GAME_MODE = "audience"  # Change to "standard" for player voting mode
    
    player = [
        ["qwen2.5-72b-instruct", "wwxq"],
        ["qwen2.5-72b-instruct", "wwxq"],
        ["qwen2.5-72b-instruct", "wwxq"]
    ]

    
    judge = [
        ["qwen2.5-72b-instruct", ""],
        # ["gpt-4.1-2025-04-14", ""]
    ]
    
    # Audience configuration (only used in audience mode)
    audience_llm = ["qwen2.5-72b-instruct", ""]
    
    # data_path = "data/word_list_1/cn_755/cn_substaintive_noun_247/Animals_16_cn.json"
    data_path = "data/word_list_1/en_628/en_substaintive_noun_220/Landforms_15_.json"
    with open(data_path, 'r', encoding='utf-8') as file:
        word_pairs = json.load(file)
    
    for j in range(1):
        for i in range(15):
            game_settings = {
                "log_folder_path": "different_size_audience", 
                "topic_category": "landforms",
                "pair": [word_pairs[i][0], word_pairs[i][1]],
                "civilian_count": 2,
                "undercover_count": 1,
                "max_statement_rounds": 10,
                "statements_per_voting": 1,
                "language": "en"
            }

            """
            Game Settings Parameters:
            
            - log_folder_path: Base folder for saving game logs
            - topic_category: Category of words used in the game
            - pair: Pair of related words from word_pairs list
            - civilian_count: Number of civilian players
            - undercover_count: Number of undercover players
            - max_statement_rounds: Maximum number of statement rounds allowed
            - statements_per_voting: Number of statement rounds before each voting
            - language: Game language (en, zh, fr, ru, es, jp, ar, de, it, pt)
            
            Game Mode Options:
            - "standard": Players vote to eliminate each other
            - "audience": Audience agent decides who to eliminate
            """
            
            game_record = run_game(
                player, 
                judge, 
                game_settings, 
                game_mode=GAME_MODE,
                audience_llm=audience_llm if GAME_MODE == "audience" else None
            )
            
            print_game_summary(game_record, game_mode=GAME_MODE)
            
            # Optional: Print the full game record in JSON format
            # print(json.dumps(game_record, indent=2, ensure_ascii=False))