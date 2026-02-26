import json
import os
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import argparse
from datetime import datetime


def load_json_files(directory_path: str) -> List[Dict]:
    """
    Intelligently traverse directory and read all JSON files

    Logic:
    1. If directory contains subdirectories with JSON files, use round-robin traversal:
       - First take the 1st JSON file from each subdirectory
       - Then take the 2nd JSON file from each subdirectory
       - Continue this pattern to ensure even data distribution
    2. If directory contains JSON files directly, traverse in filename order
    """

    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        return []

    # Collect JSON files directly in root directory
    root_json_files = []
    subdirs_with_json = {}

    # Scan root directory
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)

        if os.path.isfile(item_path) and item.endswith('.json'):
            # Root directory directly contains JSON files
            root_json_files.append(item_path)
        elif os.path.isdir(item_path):
            # Check if subdirectory contains JSON files
            json_files_in_subdir = []
            for subitem in os.listdir(item_path):
                subitem_path = os.path.join(item_path, subitem)
                if os.path.isfile(subitem_path) and subitem.endswith('.json'):
                    json_files_in_subdir.append(subitem_path)

            if json_files_in_subdir:
                # Sort by filename to ensure consistent order
                json_files_in_subdir.sort()
                subdirs_with_json[item] = json_files_in_subdir

    # Decide which traversal method to use
    if subdirs_with_json and not root_json_files:
        # Case 1: Subdirectories contain JSON, root has no JSON -> Use round-robin traversal
        print(f"Detected {len(subdirs_with_json)} subdirectories containing JSON files, using round-robin traversal")
        json_files = _round_robin_traverse(subdirs_with_json)

    elif root_json_files and not subdirs_with_json:
        # Case 2: Root directly contains JSON, no subdirectories -> Sequential traversal
        print(f"Root directory directly contains {len(root_json_files)} JSON files, using sequential traversal")
        root_json_files.sort()  # Sort by filename
        json_files = root_json_files

    elif subdirs_with_json and root_json_files:
        # Case 3: Both root JSON and subdirectory JSON exist -> Process root first, then round-robin subdirectories
        print(
            f"Root directory contains {len(root_json_files)} JSON files, {len(subdirs_with_json)} subdirectories also contain JSON")
        print("Processing order: Root JSON first, then round-robin subdirectory JSON")

        root_json_files.sort()
        subdir_json_files = _round_robin_traverse(subdirs_with_json)
        json_files = root_json_files + subdir_json_files

    else:
        # Case 4: No JSON files found
        print("No JSON files found")
        return []

    # Load and validate JSON files
    loaded_games = []
    for i, file_path in enumerate(json_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate if it's a game record format
            if 'game_record' in data:
                loaded_games.append(data['game_record'])
                print(f"[{i + 1:3d}] Loaded: {file_path}")
            else:
                print(f"[{i + 1:3d}] Skipping non-game-record file: {file_path}")

        except Exception as e:
            print(f"[{i + 1:3d}] Failed to read file {file_path}: {e}")

    return loaded_games


def _round_robin_traverse(subdirs_with_json: Dict[str, List[str]]) -> List[str]:
    """
    Round-robin traverse JSON files in multiple subdirectories

    Args:
        subdirs_with_json: {subdirectory_name: [JSON_file_path_list]}

    Returns:
        File path list after round-robin sorting
    """

    # Print subdirectory information
    for subdir, files in subdirs_with_json.items():
        print(f"  -> {subdir}: {len(files)} JSON files")

    # Find maximum number of files
    max_files = max(len(files) for files in subdirs_with_json.values())

    # Get sorted subdirectory name list (ensure consistent order)
    sorted_subdirs = sorted(subdirs_with_json.keys())

    result_files = []

    # Round-robin traversal
    for round_idx in range(max_files):
        print(f"Round {round_idx + 1} traversal:")

        for subdir in sorted_subdirs:
            files = subdirs_with_json[subdir]
            if round_idx < len(files):
                file_path = files[round_idx]
                result_files.append(file_path)
                filename = os.path.basename(file_path)
                print(f"  {subdir}: {filename}")
            else:
                print(f"  {subdir}: (no more files)")

    print(f"Round-robin complete, collected {len(result_files)} files")
    return result_files


def load_json_files_with_pattern_info(directory_path: str) -> Tuple[List[Dict], Dict]:
    """
    Load JSON files and return traversal pattern information

    Returns:
        (game_record_list, pattern_info_dict)
    """

    # Collect traversal information
    pattern_info = {
        'traversal_type': '',
        'total_files': 0,
        'subdirs_count': 0,
        'root_files_count': 0,
        'subdir_details': {}
    }

    # Check directory structure
    root_json_files = []
    subdirs_with_json = {}

    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)

        if os.path.isfile(item_path) and item.endswith('.json'):
            root_json_files.append(item_path)
        elif os.path.isdir(item_path):
            json_files_in_subdir = []
            for subitem in os.listdir(item_path):
                subitem_path = os.path.join(item_path, subitem)
                if os.path.isfile(subitem_path) and subitem.endswith('.json'):
                    json_files_in_subdir.append(subitem_path)

            if json_files_in_subdir:
                json_files_in_subdir.sort()
                subdirs_with_json[item] = json_files_in_subdir
                pattern_info['subdir_details'][item] = len(json_files_in_subdir)

    # Update pattern information
    pattern_info['root_files_count'] = len(root_json_files)
    pattern_info['subdirs_count'] = len(subdirs_with_json)

    # Determine traversal type
    if subdirs_with_json and not root_json_files:
        pattern_info['traversal_type'] = 'round_robin'
        json_files = _round_robin_traverse(subdirs_with_json)
    elif root_json_files and not subdirs_with_json:
        pattern_info['traversal_type'] = 'sequential'
        root_json_files.sort()
        json_files = root_json_files
    elif subdirs_with_json and root_json_files:
        pattern_info['traversal_type'] = 'mixed'
        root_json_files.sort()
        subdir_json_files = _round_robin_traverse(subdirs_with_json)
        json_files = root_json_files + subdir_json_files
    else:
        pattern_info['traversal_type'] = 'none'
        json_files = []

    pattern_info['total_files'] = len(json_files)

    # Load JSON files
    loaded_games = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'game_record' in data:
                loaded_games.append(data['game_record'])
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")

    return loaded_games, pattern_info


# Example: How to use the new loading function in main function
def main_with_pattern_info(data_path: str, output_path: str = None, import_previous: str = None,
                           use_alternative_expected: bool = False):
    """Main function with traversal pattern information"""

    print(f"Starting to process directory: {data_path}")

    # Use new loading function
    game_records, pattern_info = load_json_files_with_pattern_info(data_path)

    # Print traversal pattern information
    print(f"\nTraversal pattern information:")
    print(f"- Traversal type: {pattern_info['traversal_type']}")
    print(f"- Root directory JSON files: {pattern_info['root_files_count']}")
    print(f"- Subdirectories containing JSON: {pattern_info['subdirs_count']}")
    if pattern_info['subdir_details']:
        print("- Subdirectory details:")
        for subdir, count in pattern_info['subdir_details'].items():
            print(f"  * {subdir}: {count} files")
    print(f"- Total files: {pattern_info['total_files']}")

    if not game_records:
        print("No valid game record files found!")
        return

    print(f"Loaded {len(game_records)} valid game records")

    # Subsequent processing logic remains unchanged...
    # (ELO calculation logic can continue here)

    return game_records, pattern_info


# For completeness, include other parts of original code...
# (PlayerPerformance, NonZeroSumEloRatingSystem classes remain unchanged)

class PlayerPerformance:
    """Store individual player performance data in a single game"""

    def __init__(self, player_data: Dict, game_data: Dict):
        self.player_id = player_data['player_id']
        self.llm_id = player_data['llm_id']
        self.role = player_data['role']
        self.is_winner = player_data['is_winner']
        self.eliminated_round = player_data.get('eliminated_in_voting_round')

        # Calculate survival rate
        total_rounds = game_data['game_summary']['total_voting_rounds']
        if self.eliminated_round is None:
            self.survival_rate = 1.0  # Survived to the end
        else:
            self.survival_rate = (self.eliminated_round - 1) / max(total_rounds, 1)

        # Calculate voting accuracy
        self.voting_accuracy = self._calculate_voting_accuracy(game_data)

    def _calculate_voting_accuracy(self, game_data: Dict) -> float:
        """Calculate accuracy of voting against opponents"""
        votes_cast = 0
        correct_votes = 0

        # Get opponent role
        opponent_role = 'undercover' if self.role == 'civilian' else 'civilian'

        # Get opponent player ID list
        opponent_ids = {p['player_id'] for p in game_data['players'] if p['role'] == opponent_role}

        for voting_round in game_data['game_process']['voting_rounds']:
            # If eliminated before this voting round, don't count
            if (self.eliminated_round is not None and
                    voting_round['voting_round_id'] >= self.eliminated_round):
                break

            # Find this player's vote
            for vote in voting_round['votes']:
                if vote['voter_id'] == self.player_id:
                    votes_cast += 1
                    if vote['voted_for'] in opponent_ids:
                        correct_votes += 1
                    break

        return correct_votes / max(votes_cast, 1)


class NonZeroSumEloRatingSystem:
    """Non-zero-sum Elo rating system - Calculate expected and actual performance independently for each player"""

    def __init__(self, initial_rating: int = 1000, role_balance_bonus: float = 120):
        self.ratings: Dict[str, float] = defaultdict(lambda: initial_rating)
        self.game_counts: Dict[str, int] = defaultdict(int)
        self.history: List[Dict] = []
        # Role balance bonus: Give civilian bonus to balance their higher natural win rate
        self.role_balance_bonus = role_balance_bonus

    def get_k_factor(self, game_count: int) -> float:
        """
        K(g) = K_min + (K_max - K_min) * exp(- g / tau)
        """
        if game_count < 0:
            game_count = 0
        g = game_count // 12

        K_max = 60.0
        K_min = 5.0
        tau = 2.5

        k = K_min + (K_max - K_min) * math.exp(- float(g) / tau)
        return float(k)

    def calculate_performance_score(self, performance: PlayerPerformance) -> float:
        """
        Calculate player's comprehensive performance score in a single game
        Win/Loss result (75%) + Survival rate (15%) + Voting accuracy (10%)
        """
        # Basic win/loss score
        win_score = 1.0 if performance.is_winner else 0.0

        # Comprehensive score calculation
        total_score = (win_score * 0.75 +
                       performance.survival_rate * 0.15 +
                       performance.voting_accuracy * 0.10)

        return total_score

    def get_adjusted_rating(self, llm_id: str, role: str) -> float:
        """
        Get adjusted rating (used for expected score calculation)
        Give civilian role bonus to balance natural advantage
        """
        base_rating = self.ratings[llm_id]
        if role == 'civilian':
            return base_rating + self.role_balance_bonus
        else:
            return base_rating

    def calculate_individual_expected_score(self, player_perf: PlayerPerformance,
                                            all_performances: List[PlayerPerformance]) -> float:
        """
        Calculate individual player's expected performance score relative to game environment
        Based on this player's ELO difference with all other players
        """
        player_adjusted_rating = self.get_adjusted_rating(player_perf.llm_id, player_perf.role)

        # Calculate expected win rate against all other players, then take average
        expected_scores = []

        for other_perf in all_performances:
            if other_perf.llm_id != player_perf.llm_id:
                other_adjusted_rating = self.get_adjusted_rating(other_perf.llm_id, other_perf.role)
                # Calculate expected win rate against this opponent
                expected_vs_other = 1 / (1 + 10 ** ((other_adjusted_rating - player_adjusted_rating) / 400))
                expected_scores.append(expected_vs_other)

        # Return average expected score
        return sum(expected_scores) / len(expected_scores) if expected_scores else 0.5

    def calculate_role_based_expected_score(self, player_perf: PlayerPerformance,
                                            all_performances: List[PlayerPerformance]) -> float:
        """
        Role-based expected performance score calculation
        Consider natural win rate differences between roles
        """
        # Base expected score (based on role)
        if player_perf.role == 'civilian':
            # Civilian has higher base expectation (due to numbers and information advantage)
            base_expected = 0.65
        else:  # undercover
            # Undercover has lower base expectation (but requires higher skill)
            base_expected = 0.35

        # Adjustment combining ELO relative strength
        elo_expected = self.calculate_individual_expected_score(player_perf, all_performances)

        # Weighted average: Base expectation 70% + ELO expectation 30%
        final_expected = base_expected * 0.7 + elo_expected * 0.3

        return final_expected

    def update_ratings_non_zero_sum(self, game_performances: List[PlayerPerformance]):
        """
        Non-zero-sum rating update: Calculate expected and actual performance independently for each player
        Does not force total score change to be zero
        """
        update_details = []

        for player_perf in game_performances:
            # Calculate this player's expected performance score
            expected_score = self.calculate_role_based_expected_score(player_perf, game_performances)

            # Calculate actual performance score
            actual_score = self.calculate_performance_score(player_perf)

            # Get this player's K value
            k_factor = self.get_k_factor(self.game_counts[player_perf.llm_id])

            # Calculate rating change: ΔR = K * (S - E)
            rating_change = k_factor * (actual_score - expected_score)

            # Update rating
            old_rating = self.ratings[player_perf.llm_id]
            self.ratings[player_perf.llm_id] += rating_change
            self.game_counts[player_perf.llm_id] += 1

            # Record detailed information
            update_details.append({
                'llm_id': player_perf.llm_id,
                'role': player_perf.role,
                'old_rating': old_rating,
                'new_rating': self.ratings[player_perf.llm_id],
                'rating_change': rating_change,
                'expected_score': expected_score,
                'actual_score': actual_score,
                'k_factor': k_factor,
                'performance_breakdown': {
                    'win_score': 1.0 if player_perf.is_winner else 0.0,
                    'survival_rate': player_perf.survival_rate,
                    'voting_accuracy': player_perf.voting_accuracy
                }
            })

        return update_details

    def calculate_alternative_expected_score(self, player_perf: PlayerPerformance,
                                             all_performances: List[PlayerPerformance]) -> float:
        """
        Alternative expected score calculation method: Based on team average strength difference
        """
        # Divide teams
        civilian_team = [p for p in all_performances if p.role == 'civilian']
        undercover_team = [p for p in all_performances if p.role == 'undercover']

        if not civilian_team or not undercover_team:
            return 0.5  # If teams are incomplete, return neutral expectation

        # Calculate team average ELO
        civilian_avg_rating = sum(self.get_adjusted_rating(p.llm_id, p.role) for p in civilian_team) / len(
            civilian_team)
        undercover_avg_rating = sum(self.get_adjusted_rating(p.llm_id, p.role) for p in undercover_team) / len(
            undercover_team)

        # Calculate team win rates
        civilian_team_expected = 1 / (1 + 10 ** ((undercover_avg_rating - civilian_avg_rating) / 400))
        undercover_team_expected = 1 - civilian_team_expected

        # Return corresponding team expected win rate based on player role
        if player_perf.role == 'civilian':
            return civilian_team_expected
        else:
            return undercover_team_expected

    def process_game(self, game_data: Dict, use_alternative_expected: bool = False) -> Dict:
        """Process single game data"""
        # Parse player performances
        performances = []
        for player_data in game_data['players']:
            perf = PlayerPerformance(player_data, game_data)
            performances.append(perf)

        # If using alternative expected calculation method
        if use_alternative_expected:
            # Temporarily modify expected calculation method
            original_method = self.calculate_role_based_expected_score
            self.calculate_role_based_expected_score = self.calculate_alternative_expected_score

        # Use non-zero-sum update method
        update_details = self.update_ratings_non_zero_sum(performances)

        # Restore original method
        if use_alternative_expected:
            self.calculate_role_based_expected_score = original_method

        if update_details is None:
            return None  # Game data has issues, skip

        # Calculate total rating change (for monitoring system balance)
        total_rating_change = sum(detail['rating_change'] for detail in update_details)

        # Record history
        game_record = {
            'game_id': game_data['game_id'],
            'timestamp': game_data['timestamp'],
            'system_info': {
                'total_rating_change': total_rating_change,
                'average_rating_change': total_rating_change / len(update_details) if update_details else 0,
                'use_alternative_expected': use_alternative_expected
            },
            'players': [],
            'rating_changes': {}
        }

        for i, perf in enumerate(performances):
            detail = update_details[i]

            # Calculate adjusted rating (for display)
            adjusted_old_rating = detail['old_rating']
            if perf.role == 'civilian':
                adjusted_old_rating += self.role_balance_bonus

            adjusted_new_rating = detail['new_rating']
            if perf.role == 'civilian':
                adjusted_new_rating += self.role_balance_bonus

            player_record = {
                'llm_id': perf.llm_id,
                'role': perf.role,
                'is_winner': perf.is_winner,
                'survival_rate': perf.survival_rate,
                'voting_accuracy': perf.voting_accuracy,
                'performance_score': detail['actual_score'],
                'expected_score': detail['expected_score'],
                'old_rating': detail['old_rating'],
                'new_rating': detail['new_rating'],
                'adjusted_old_rating': adjusted_old_rating,
                'adjusted_new_rating': adjusted_new_rating,
                'rating_change': detail['rating_change'],
                'k_factor': detail['k_factor'],
                'performance_breakdown': detail['performance_breakdown']
            }
            game_record['players'].append(player_record)
            game_record['rating_changes'][perf.llm_id] = detail['rating_change']

        self.history.append(game_record)
        return game_record

def main(data_path: str, output_path: str = None, import_previous: str = None, use_alternative_expected: bool = False):


    game_records, pattern_info = load_json_files_with_pattern_info(data_path)
    
    game_records.sort(key=lambda x: x['timestamp'])
    
    elo_system = NonZeroSumEloRatingSystem(role_balance_bonus=115)
    
    if import_previous and os.path.exists(import_previous):
        try:
            with open(import_previous, 'r', encoding='utf-8') as f:
                previous_data = json.load(f)
                
            for rating_data in previous_data.get('final_ratings', []):
                llm_id = rating_data['llm_id']
                elo_system.ratings[llm_id] = rating_data['rating']
                elo_system.game_counts[llm_id] = rating_data['games_played']
            

            if 'game_history' in previous_data:
                elo_system.history = previous_data['game_history']
                print(f"log {len(elo_system.history)} ")
            
            print(f"log {len(previous_data.get('final_ratings', []))}")
        except Exception as e:
            print(f"log fail: {e}")

    processed_games = []
    total_rating_changes = []

    initial_history_count = len(elo_system.history)

    processed_game_ids = {record['game_id'] for record in elo_system.history}
    
    for i, game_data in enumerate(game_records, 1):
        try:
            if game_data['game_id'] in processed_game_ids:
                continue
                
            game_record = elo_system.process_game(game_data, use_alternative_expected)
            if game_record is not None:
                processed_games.append(game_record)
                total_rating_changes.append(game_record['system_info']['total_rating_change'])
                processed_game_ids.add(game_data['game_id'])

        except Exception as e:
            print(f"log fail {game_data.get('game_id', 'unknown')}: {e}")
    

    
    final_ratings = []
    llm_stats = defaultdict(list)

    for game_record in elo_system.history:
        for player_record in game_record['players']:
            llm_stats[player_record['llm_id']].append(player_record)

    for llm_id, ratings in elo_system.ratings.items():
        stats = llm_stats.get(llm_id, [])
        
        if stats:
            total_games = len(stats)
            wins = sum(1 for s in stats if s['is_winner'])
            win_rate = wins / total_games if total_games > 0 else 0
            
            civilian_games = [s for s in stats if s['role'] == 'civilian']
            undercover_games = [s for s in stats if s['role'] == 'undercover']
            
            civilian_wins = sum(1 for s in civilian_games if s['is_winner'])
            undercover_wins = sum(1 for s in undercover_games if s['is_winner'])
            
            civilian_win_rate = civilian_wins / len(civilian_games) if civilian_games else 0
            undercover_win_rate = undercover_wins / len(undercover_games) if undercover_games else 0
            
            avg_survival_rate = sum(s['survival_rate'] for s in stats) / total_games
            avg_voting_accuracy = sum(s['voting_accuracy'] for s in stats) / total_games
            avg_performance_score = sum(s['performance_score'] for s in stats) / total_games
            avg_expected_score = sum(s['expected_score'] for s in stats) / total_games
            avg_rating_change = sum(s['rating_change'] for s in stats) / total_games
            
        else:
            total_games = 0
            win_rate = 0
            civilian_win_rate = 0
            undercover_win_rate = 0
            avg_survival_rate = 0
            avg_voting_accuracy = 0
            avg_performance_score = 0
            avg_expected_score = 0
            avg_rating_change = 0

        final_ratings.append({
            'llm_id': llm_id,
            'rating': round(ratings, 2),
            'games_played': elo_system.game_counts[llm_id],
            'k_factor': elo_system.get_k_factor(elo_system.game_counts[llm_id]),
            'win_rate': round(win_rate, 3),
            'civilian_win_rate': round(civilian_win_rate, 3) if civilian_games else 0,
            'undercover_win_rate': round(undercover_win_rate, 3) if undercover_games else 0,
            'civilian_games': len(civilian_games) if 'civilian_games' in locals() else 0,
            'undercover_games': len(undercover_games) if 'undercover_games' in locals() else 0,
            'avg_survival_rate': round(avg_survival_rate, 3),
            'avg_voting_accuracy': round(avg_voting_accuracy, 3),
            'avg_performance_score': round(avg_performance_score, 3),
            'avg_expected_score': round(avg_expected_score, 3),
            'avg_rating_change': round(avg_rating_change, 3)
        })


    final_ratings.sort(key=lambda x: x['rating'], reverse=True)
    
    for rank, data in enumerate(final_ratings, 1):
        print(f"{rank:<5}{data['llm_id']:<25}{data['rating']:<8.2f}"
              f"{data['games_played']:<6}{data['win_rate']:<6.3f}"
              f"{data['civilian_win_rate']:<8.3f}{data['undercover_win_rate']:<8.3f}"
              f"{data['avg_expected_score']:<8.3f}{data['avg_performance_score']:<8.3f}"
              f"{data['avg_rating_change']:<9.3f}{data['k_factor']:<6.1f}")
    

    if output_path:
        result = {
            'final_ratings': final_ratings,
            'game_history': elo_system.history,
            'traversal_info': pattern_info,
            'statistics': {
                'total_games': len(processed_games),
                'total_players': len(final_ratings),
                'role_balance_bonus': elo_system.role_balance_bonus,
                'system_type': 'non_zero_sum_elo',
                'use_alternative_expected': use_alternative_expected,
                'performance_weights': {
                    'win_loss': 0.75,
                    'survival_rate': 0.15,
                    'voting_accuracy': 0.10
                },
                'non_zero_sum_analysis': {
                    'avg_total_rating_change_per_game': avg_total_change if total_rating_changes else 0,
                    'max_total_rating_change': max_total_change if total_rating_changes else 0,
                    'min_total_rating_change': min_total_change if total_rating_changes else 0
                },
                'processing_timestamp': datetime.now().isoformat()
            }
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n详细结果已保存至: {output_path}")
    
    return final_ratings, elo_system.history

if __name__ == "__main__":

    data_path = ""
    output_path = ""
    import_previous = ""
    use_alternative_expected = True
    
    main(
        data_path,
        output_path,
        import_previous,
        use_alternative_expected
    )