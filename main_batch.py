import json
import os
import datetime
import time
import traceback
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
# from undercover.game import UndercoverGame
from undercover.game import UndercoverGame
from undercover_audience.game import UndercoverAudienceGame
from undercover.agents.player_agent import LLMPlayer
from undercover.agents.judge_agent import LLMJudge
from undercover_audience.agents.audience_agent import LLMAudience
from undercover_audience.agents.player_agent import LLMPlayerAU
from undercover_audience.agents.judge_agent import LLMJudgeAU


class BatchGameRunner:
    """Batch Game Runner - Supports parallel processing"""

    def __init__(self):
        self.game_results = []
        self.failed_games = []
        self.start_time = None
        self.results_lock = threading.Lock()

    def run_single_game(self, players, judges, game_settings, game_mode="standard", audience_llm=None):
        """
        Run a single game

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

            if audience_llm is None:
                audience_llm = ["claude-3-7-sonnet-20250219", ""]
            audience = LLMAudience("audience-1", audience_llm[0], game_settings["language"])
            game = UndercoverAudienceGame(
                **game_params,
                audience=audience
            )
        else:

            game = UndercoverGame(**game_params)

        # Run game
        game.run_game()

        # Save game record
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        thread_id = threading.current_thread().ident
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)


        tag_dir = os.path.join(logs_dir, f"{game_settings['log_folder_path']}_{game_mode}")
        if not os.path.exists(tag_dir):
            os.makedirs(tag_dir)

        language_dir = os.path.join(tag_dir, game_settings["language"])
        if not os.path.exists(language_dir):
            os.makedirs(language_dir)

        topic_dir = os.path.join(language_dir, game_settings["topic_category"])
        if not os.path.exists(topic_dir):
            os.makedirs(topic_dir)


        filename = f"{game_settings['pair'][0]}_{game_settings['pair'][1]}_{timestamp}_{thread_id}.json"
        file_path = os.path.join(topic_dir, filename)

        # Save game record
        game.save_game_record(file_path)

        return game.get_game_record()

    def run_single_word_pair(self, word_pair, pair_idx, players, judges, base_game_settings, batch_config):
        """Run all rounds for a single word pair"""
        rounds_per_pair = batch_config.get("rounds_per_pair", 1)
        game_mode = batch_config.get("game_mode", "standard")
        audience_llm = batch_config.get("audience_llm", None)
        max_retries = batch_config.get("max_retries", 2)

        pair_results = []
        pair_failures = []
        thread_name = threading.current_thread().name

        print(f"\n[Thread-{thread_name}] Started processing word pair {pair_idx + 1}: {word_pair[0]} vs {word_pair[1]}")

        for round_idx in range(rounds_per_pair):
            game_number = pair_idx * rounds_per_pair + round_idx + 1

            # Prepare game settings
            game_settings = base_game_settings.copy()
            game_settings["pair"] = [word_pair[0], word_pair[1]]

            # Try to run the game
            success = False
            for retry in range(max_retries + 1):
                try:
                    if retry > 0:
                        print(
                            f"    [Thread-{thread_name}] Word pair {pair_idx + 1} round {round_idx + 1} retry attempt {retry}...")
                        time.sleep(2)

                    game_record = self.run_single_game(
                        players, judges, game_settings,
                        game_mode=game_mode, audience_llm=audience_llm
                    )
                    success = True
                    result_info = {
                        "game_number": game_number,
                        "pair_index": pair_idx,
                        "round_index": round_idx,
                        "word_pair": word_pair,
                        "game_record": game_record,
                        "thread_name": thread_name,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    pair_results.append(result_info)

                    print(f"    [Thread-{thread_name}] ✓ Word pair {pair_idx + 1} round {round_idx + 1} completed")

                    break

                except Exception as e:
                    error_info = {
                        "game_number": game_number,
                        "pair_index": pair_idx,
                        "round_index": round_idx,
                        "word_pair": word_pair,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "retry_attempt": retry,
                        "thread_name": thread_name,
                        "timestamp": datetime.datetime.now().isoformat()
                    }

                    if retry == max_retries:
                        pair_failures.append(error_info)
                        print(
                            f"    [Thread-{thread_name}] ✗ Word pair {pair_idx + 1} round {round_idx + 1} final failure: {str(e)}")

        print(
            f"[Thread-{thread_name}] Word pair {pair_idx + 1} all rounds completed, {len(pair_results)} successful, {len(pair_failures)} failed")
        return pair_results, pair_failures

    def run_batch_games_parallel(self,
                                 players: List,
                                 judges: List,
                                 base_game_settings: Dict[str, Any],
                                 word_pairs: List,
                                 batch_config: Dict[str, Any]):
        """
        Run batch games in parallel

        New parameters in batch_config:
            - max_workers: Maximum concurrent threads (default 3)
            - chunk_size: Number of word pairs per batch (default all)
        """
        self.start_time = time.time()

        max_workers = batch_config.get("max_workers", 3)  # Default 3 concurrent threads
        chunk_size = batch_config.get("chunk_size", len(word_pairs))  # Batch size
        rounds_per_pair = batch_config.get("rounds_per_pair", 1)

        total_games = len(word_pairs) * rounds_per_pair
        completed_games = 0

        # Process word pairs in chunks
        for chunk_start in range(0, len(word_pairs), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(word_pairs))
            chunk_pairs = word_pairs[chunk_start:chunk_end]

            print(f"\n📋 Processing word pair batch: {chunk_start + 1}-{chunk_end} ({len(chunk_pairs)} pairs)")


            with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="GameWorker") as executor:
                future_to_pair = {
                    executor.submit(
                        self.run_single_word_pair,
                        word_pair,
                        chunk_start + i,
                        players,
                        judges,
                        base_game_settings,
                        batch_config
                    ): (chunk_start + i, word_pair)
                    for i, word_pair in enumerate(chunk_pairs)
                }


                chunk_completed = 0
                for future in as_completed(future_to_pair):
                    pair_idx, word_pair = future_to_pair[future]
                    try:
                        pair_results, pair_failures = future.result()

                        with self.results_lock:
                            self.game_results.extend(pair_results)
                            self.failed_games.extend(pair_failures)
                            completed_games += len(pair_results)

                        chunk_completed += 1
                        print(
                            f"Word pair {pair_idx + 1} ({word_pair[0]} vs {word_pair[1]}) processing completed ({chunk_completed}/{len(chunk_pairs)})")

                    except Exception as e:
                        print(f"Word pair {pair_idx + 1} processing error: {str(e)}")
                        with self.results_lock:
                            error_info = {
                                "pair_index": pair_idx,
                                "word_pair": word_pair,
                                "error": f"Thread execution failed: {str(e)}",
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                            self.failed_games.append(error_info)

            print(f"Batch {chunk_start + 1}-{chunk_end} processing completed")

        return self._generate_batch_summary(completed_games, total_games)

    def run_batch_games(self,
                        players: List,
                        judges: List,
                        base_game_settings: Dict[str, Any],
                        word_pairs: List,
                        batch_config: Dict[str, Any]):
        """
        Original serial batch game execution (kept for backward compatibility)
        """
        self.start_time = time.time()

        rounds_per_pair = batch_config.get("rounds_per_pair", 1)
        game_mode = batch_config.get("game_mode", "standard")
        audience_llm = batch_config.get("audience_llm", None)
        delay_between_games = batch_config.get("delay_between_games", 0)
        max_retries = batch_config.get("max_retries", 2)
        continue_on_error = batch_config.get("continue_on_error", True)

        total_games = len(word_pairs) * rounds_per_pair
        completed_games = 0


        for pair_idx, word_pair in enumerate(word_pairs):
            print(f"\nProcessing word pair {pair_idx + 1}/{len(word_pairs)}: {word_pair[0]} vs {word_pair[1]}")

            for round_idx in range(rounds_per_pair):
                game_number = pair_idx * rounds_per_pair + round_idx + 1
                print(
                    f"  Running round {round_idx + 1}/{rounds_per_pair} (Total progress: {game_number}/{total_games})")

                # Prepare game settings
                game_settings = base_game_settings.copy()
                game_settings["pair"] = [word_pair[0], word_pair[1]]

                # Try to run the game with retry mechanism
                success = False
                for retry in range(max_retries + 1):
                    try:
                        if retry > 0:
                            print(f"    Retry attempt {retry}...")
                            time.sleep(2)  # Wait before retry

                        game_record = self.run_single_game(
                            players,
                            judges,
                            game_settings,
                            game_mode=game_mode,
                            audience_llm=audience_llm
                        )

                        # Record successful game
                        result_info = {
                            "game_number": game_number,
                            "pair_index": pair_idx,
                            "round_index": round_idx,
                            "word_pair": word_pair,
                            "game_record": game_record,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        self.game_results.append(result_info)

                        self.print_game_summary(game_record, game_mode, game_number, total_games)
                        completed_games += 1
                        success = True
                        break

                    except Exception as e:
                        error_info = {
                            "game_number": game_number,
                            "pair_index": pair_idx,
                            "round_index": round_idx,
                            "word_pair": word_pair,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                            "retry_attempt": retry,
                            "timestamp": datetime.datetime.now().isoformat()
                        }

                        print(f"    Game {game_number} error (attempt {retry + 1}/{max_retries + 1}): {str(e)}")

                        if retry == max_retries:
                            self.failed_games.append(error_info)
                            if not continue_on_error:
                                print(f"\nGame {game_number} failed, stopping batch execution11111111111")
                                return self._generate_batch_summary(completed_games, total_games)
                            else:
                                print(f"    Game {game_number} final failure, continuing to next g")

                # Delay between games
                if delay_between_games > 0 and game_number < total_games:
                    print(f"    Waiting {delay_between_games} seconds...")
                    time.sleep(delay_between_games)

        return self._generate_batch_summary(completed_games, total_games)

    def _generate_batch_summary(self, completed_games: int, total_games: int) -> Dict[str, Any]:
        """Generate batch execution summary"""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0

        summary = {
            "total_games": total_games,
            "completed_games": completed_games,
            "failed_games": len(self.failed_games),
            "success_rate": completed_games / total_games if total_games > 0 else 0,
            "duration_seconds": duration,
            "duration_formatted": self._format_duration(duration),
            "games_per_minute": (completed_games / duration * 60) if duration > 0 else 0,
            "failed_game_details": self.failed_games
        }

        self._print_batch_summary(summary)
        return summary

    def _format_duration(self, seconds: float) -> str:
        """Format time duration"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _print_batch_summary(self, summary: Dict[str, Any]):
        """Print batch execution summary"""
        print(f"\n{'=' * 50}")
        print(f"🏁 Batch game execution completed")

        if summary['failed_games'] > 0:
            print(f"\nFailed games:")
            for failed in summary['failed_game_details']:
                print(f"  Game {failed.get('game_number', '?')}: {failed['word_pair']} - {failed['error']}")

        print(f"{'=' * 70}\n")

    def print_game_summary(self, game_record, game_mode="standard", game_number=None, total_games=None):
        """
        Print single game summary
        """
        record = game_record["game_record"]

        progress_info = ""
        if game_number and total_games:
            progress_info = f" ({game_number}/{total_games})"

        print(f"\n{'=' * 50}")
        print(f"Game ID: {record['game_id']}{progress_info}")
        print(f"Game mode: {game_mode.upper()}")
        print(f"Topic: {record['topic_category']}")
        print(f"Concept: {record['concept_pair']['concept_a']} vs {record['concept_pair']['concept_b']}")
        print(f"{'=' * 50}")

    def save_batch_results(self, output_file: Optional[str] = None):
        """Save batch execution results"""
        logs_dir = os.path.join(os.path.dirname(__file__), "logs_log")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        if output_file is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(logs_dir, f"batch_results_{timestamp}.json")
        else:
            # If a file path is provided, ensure it's in the logs_log directory
            if not os.path.isabs(output_file):
                output_file = os.path.join(logs_dir, output_file)

        results = {
            "batch_summary": self._generate_batch_summary(len(self.game_results),
                                                          len(self.game_results) + len(self.failed_games)),
            "successful_games": self.game_results,
            "failed_games": self.failed_games
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Batch results saved to: {output_file}")


def main():
    """Main function"""

    # Create batch runner
    runner = BatchGameRunner()


    players = [

    ]



    judges = [
    ]

    # Base game settings
    base_game_settings = {
        "log_folder_path": "iclr",
        "topic_category": "",
        "civilian_count": 4,
        "undercover_count": 2,
        "max_statement_rounds": 5,
        "statements_per_voting": 1,
        "language": "en"
    }

    # Parallel batch configuration
    batch_config = {
        "rounds_per_pair": 1,  # Run 1 round per word pair
        "game_mode": "standard",  # Game mode
        "audience_llm": ["gpt-4-0125-preview", ""],
        "delay_between_games": 0,  # No delay needed for parallel execution
        "max_retries": 2,  # Maximum 2 retries
        "continue_on_error": True,  # Continue on error
        "max_workers": 3,  # 
        "chunk_size": 6  # 
    }

    # Load word pairs
    data_path = ""
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            word_pairs = json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found {data_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON file {data_path}")
        return

    # Can choose to run only the first N word pairs for testing
    word_pairs = word_pairs[:6]

    print(f"Loaded {len(word_pairs)} word pairs")

    # Run parallel batch games
    try:
        print("Running games in parallel mode...")
        batch_summary = runner.run_batch_games_parallel(  #  Use parallel version
            players=players,
            judges=judges,
            base_game_settings=base_game_settings,
            word_pairs=word_pairs,
            batch_config=batch_config
        )

        # Save results
        runner.save_batch_results()

    except KeyboardInterrupt:
        print("\n\n️  User interrupted batch execution")
        print("Saving completed game results...")
        runner.save_batch_results("interrupted_batch_results.json")
    except Exception as e:
        print(f"\n\n Serious error in batch execution: {str(e)}")
        print("Saving completed game results...")
        runner.save_batch_results("error_batch_results.json")
        traceback.print_exc()


if __name__ == "__main__":
    main()