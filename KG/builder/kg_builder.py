"""
Universal Knowledge Graph builder from game logs.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: networkx not available. Install with: pip install networkx")

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import (
    NodeType, EdgeType, Feature, ConceptNode, FeatureNode, Edge,
    StatementRecord, GameRecord, KnowledgeGraphData
)
from icml_exp.KG.extraction.nlp_extractor import NLPFeatureExtractor
from icml_exp.KG.extraction.keyword_extractor import KeywordExtractor
from icml_exp.KG.extraction.feature_merger import FeatureMerger


class KnowledgeGraphBuilder:
    """Build knowledge graphs from Undercover game logs."""

    # Node colors
    COLORS = {
        "concept_a": "#2E8B57",  # Sea green (civilian concept)
        "concept_b": "#FFD700",  # Gold (undercover concept)
        "feature_shared": "#87CEEB",  # Sky blue (shared features)
        "feature_a_only": "#98FB98",  # Pale green
        "feature_b_only": "#F0E68C",  # Khaki
        "category": "#DDA0DD"  # Plum
    }

    def __init__(
        self,
        language: str = "en",
        use_nlp: bool = True,
        min_feature_frequency: int = 1,
        relevance_threshold: float = 0.3,
        merge_similar: bool = True,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize the KG builder.

        Args:
            language: Language code for NLP processing
            use_nlp: Whether to use spaCy NLP extraction
            min_feature_frequency: Minimum frequency to include a feature
            relevance_threshold: Minimum relevance score for feature extraction
            merge_similar: Whether to merge similar features
            similarity_threshold: Threshold for feature similarity
        """
        self.language = language
        self.use_nlp = use_nlp
        self.min_feature_frequency = min_feature_frequency
        self.relevance_threshold = relevance_threshold
        self.merge_similar = merge_similar

        # Initialize extractors
        if use_nlp:
            self.extractor = NLPFeatureExtractor(language=language)
        else:
            self.extractor = KeywordExtractor(language=language)

        self.merger = FeatureMerger(similarity_threshold=similarity_threshold)

        # Data storage
        self.kg_data = KnowledgeGraphData()
        self.game_records: List[GameRecord] = []

    def load_logs(
        self,
        log_path: str,
        max_files: Optional[int] = None,
        category_filter: Optional[str] = None
    ) -> List[GameRecord]:
        """
        Load game logs from a directory or file.

        Args:
            log_path: Path to log file or directory
            max_files: Maximum number of files to load
            category_filter: Only load logs from this category

        Returns:
            List of parsed GameRecord objects
        """
        log_path = Path(log_path)
        records = []

        if log_path.is_file():
            record = self._load_single_log(log_path)
            if record:
                records.append(record)
        else:
            # Recursively find all JSON files
            json_files = list(log_path.rglob("*.json"))

            if max_files:
                json_files = json_files[:max_files]

            for file_path in json_files:
                # Check category filter
                if category_filter:
                    if category_filter not in str(file_path):
                        continue

                record = self._load_single_log(file_path)
                if record:
                    records.append(record)

        self.game_records = records
        return records

    def _load_single_log(self, file_path: Path) -> Optional[GameRecord]:
        """Load and parse a single game log file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle nested game_record structure
            if 'game_record' in data:
                data = data['game_record']

            # Extract basic info
            game_id = data.get('game_id', str(file_path.stem))
            category = data.get('topic_category', 'unknown')

            concept_pair = data.get('concept_pair', {})
            concept_a = concept_pair.get('concept_a', '')
            concept_b = concept_pair.get('concept_b', '')

            if not concept_a or not concept_b:
                return None

            # Get winner info
            summary = data.get('game_summary', {})
            winner_role = summary.get('winner_role', 'unknown')

            # Build player mapping (player_id -> assigned_concept)
            player_concepts = {}
            player_roles = {}
            for player in data.get('players', []):
                player_id = player.get('player_id')
                player_concepts[player_id] = player.get('assigned_concept', '')
                player_roles[player_id] = player.get('role', '')

            # Extract statements
            statements = []
            game_process = data.get('game_process', {})
            for stmt in game_process.get('statements', []):
                player_id = stmt.get('player_id')

                # Get metrics
                metrics = stmt.get('metrics', {})
                judges_stats = metrics.get('judges_stats', {})

                statement_record = StatementRecord(
                    statement_id=stmt.get('statement_id', 0),
                    player_id=player_id,
                    llm_id=stmt.get('llm_id', ''),
                    content=stmt.get('content', ''),
                    statement_round=stmt.get('statement_round', 0),
                    assigned_concept=player_concepts.get(player_id, ''),
                    role=player_roles.get(player_id, ''),
                    novelty_score=judges_stats.get('novelty_score_mean', 0.0),
                    relevance_score=judges_stats.get('relevance_score_mean', 0.0),
                    reasonableness_score=judges_stats.get('reasonableness_score_mean', 0.0)
                )
                statements.append(statement_record)

            return GameRecord(
                game_id=game_id,
                category=category,
                concept_a=concept_a,
                concept_b=concept_b,
                winner_role=winner_role,
                statements=statements
            )

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def build_graph(self, records: Optional[List[GameRecord]] = None) -> 'nx.Graph':
        """
        Build a NetworkX graph from game records.

        Args:
            records: Game records to process (uses self.game_records if None)

        Returns:
            NetworkX graph object
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx is required for graph building")

        if records is None:
            records = self.game_records

        if not records:
            raise ValueError("No game records to process")

        # Reset KG data
        self.kg_data = KnowledgeGraphData()

        # Process each game
        for record in records:
            self._process_game_record(record)

        # Merge similar features if enabled
        if self.merge_similar:
            self._merge_similar_features()

        # Build NetworkX graph
        return self._build_networkx_graph()

    def _process_game_record(self, record: GameRecord):
        """Process a single game record."""
        # Update concept nodes
        for concept_name in [record.concept_a, record.concept_b]:
            if concept_name not in self.kg_data.concepts:
                self.kg_data.concepts[concept_name] = ConceptNode(
                    name=concept_name,
                    category=record.category,
                    appearances=0,
                    wins=0
                )

            node = self.kg_data.concepts[concept_name]
            node.appearances += 1
            if (concept_name == record.concept_a and record.winner_role == "civilian") or \
               (concept_name == record.concept_b and record.winner_role == "undercover"):
                node.wins += 1

        # Extract features from statements
        concept_features = defaultdict(list)
        concept_statements = defaultdict(list)
        feature_weights = defaultdict(lambda: defaultdict(float))

        for stmt in record.statements:
            if not stmt.content or stmt.relevance_score < self.relevance_threshold:
                continue

            concept = stmt.assigned_concept
            concept_statements[concept].append(stmt.content)

            # Extract features
            features = self.extractor.extract_features(stmt.content)
            for feature in features:
                concept_features[concept].append(feature)
                # Weight by relevance score
                feature_weights[concept][feature.text.lower()] += stmt.relevance_score

        # Add features to concept nodes
        for concept, features in concept_features.items():
            if concept in self.kg_data.concepts:
                self.kg_data.concepts[concept].features.extend(
                    [f.text for f in features]
                )
                self.kg_data.concepts[concept].statements.extend(
                    concept_statements[concept]
                )

        # Create/update feature nodes
        for concept, features in concept_features.items():
            for feature in features:
                feature_key = feature.text.lower()
                weight = feature_weights[concept].get(feature_key, 1.0)

                if feature_key not in self.kg_data.features:
                    self.kg_data.features[feature_key] = FeatureNode(
                        name=feature.text,
                        feature_type=feature.feature_type,
                        frequency=0,
                        avg_relevance=0.0,
                        concepts=[]
                    )

                node = self.kg_data.features[feature_key]
                node.frequency += 1
                # Rolling average
                node.avg_relevance = (
                    (node.avg_relevance * (node.frequency - 1) + weight) / node.frequency
                )
                if concept not in node.concepts:
                    node.concepts.append(concept)

    def _merge_similar_features(self):
        """Merge similar features across the graph."""
        features_list = list(self.kg_data.features.values())
        if not features_list:
            return

        # Create Feature objects for merger
        feature_objs = [
            Feature(text=f.name, feature_type=f.feature_type)
            for f in features_list
        ]
        weights = {f.name.lower(): f.avg_relevance for f in features_list}

        merged = self.merger.merge_features(feature_objs, weights)

        # Rebuild features dict with merged nodes
        new_features = {}
        for merged_node in merged:
            key = merged_node.name.lower()
            # Collect all concepts from variants
            all_concepts = set()
            total_freq = 0
            for variant in merged_node.metadata.get('variants', [merged_node.name]):
                old_key = variant.lower()
                if old_key in self.kg_data.features:
                    old_node = self.kg_data.features[old_key]
                    all_concepts.update(old_node.concepts)
                    total_freq += old_node.frequency

            merged_node.concepts = list(all_concepts)
            merged_node.frequency = max(merged_node.frequency, total_freq)
            new_features[key] = merged_node

        self.kg_data.features = new_features

    def _build_networkx_graph(self) -> 'nx.Graph':
        """Build a NetworkX graph from KG data."""
        G = nx.Graph()

        # Add concept nodes
        for concept_name, concept_node in self.kg_data.concepts.items():
            G.add_node(
                concept_name,
                node_type=NodeType.CONCEPT.value,
                category=concept_node.category,
                appearances=concept_node.appearances,
                wins=concept_node.wins,
                win_rate=concept_node.win_rate,
                color=self.COLORS["concept_a"],  # Will be updated for pairs
                size=40
            )

        # Add feature nodes (filtered by frequency)
        for feature_key, feature_node in self.kg_data.features.items():
            if feature_node.frequency < self.min_feature_frequency:
                continue

            # Determine color based on which concepts share this feature
            if feature_node.is_shared:
                color = self.COLORS["feature_shared"]
            else:
                # Single concept feature - color based on concept
                color = self.COLORS["feature_a_only"]  # Default

            G.add_node(
                feature_node.name,
                node_type=NodeType.FEATURE.value,
                feature_type=feature_node.feature_type,
                frequency=feature_node.frequency,
                avg_relevance=feature_node.avg_relevance,
                is_shared=feature_node.is_shared,
                is_distinguishing=feature_node.is_distinguishing,
                color=color,
                size=15 + min(feature_node.frequency * 2, 25)
            )

            # Add edges from concept to feature
            for concept in feature_node.concepts:
                if concept in G.nodes():
                    edge_type = EdgeType.HAS_FEATURE.value
                    G.add_edge(
                        concept,
                        feature_node.name,
                        edge_type=edge_type,
                        weight=feature_node.avg_relevance
                    )

        return G

    def build_from_logs(
        self,
        log_path: str,
        max_files: Optional[int] = None,
        category_filter: Optional[str] = None
    ) -> 'nx.Graph':
        """
        Convenience method to load logs and build graph in one step.

        Args:
            log_path: Path to log file or directory
            max_files: Maximum number of files to load
            category_filter: Only load logs from this category

        Returns:
            NetworkX graph object
        """
        self.load_logs(log_path, max_files, category_filter)
        return self.build_graph()

    def get_concept_pair_subgraph(
        self,
        concept_a: str,
        concept_b: str,
        graph: Optional['nx.Graph'] = None
    ) -> 'nx.Graph':
        """
        Extract a subgraph for a specific concept pair.

        Args:
            concept_a: First concept name
            concept_b: Second concept name
            graph: Full graph (builds new one if None)

        Returns:
            Subgraph containing only nodes related to the concept pair
        """
        if graph is None:
            graph = self.build_graph()

        # Get all features connected to either concept
        relevant_nodes = {concept_a, concept_b}

        for concept in [concept_a, concept_b]:
            if concept in graph:
                neighbors = list(graph.neighbors(concept))
                relevant_nodes.update(neighbors)

        return graph.subgraph(relevant_nodes).copy()

    def get_graph_statistics(self, graph: 'nx.Graph') -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.

        Args:
            graph: NetworkX graph

        Returns:
            Dictionary of statistics
        """
        concept_nodes = [n for n, d in graph.nodes(data=True)
                        if d.get('node_type') == NodeType.CONCEPT.value]
        feature_nodes = [n for n, d in graph.nodes(data=True)
                        if d.get('node_type') == NodeType.FEATURE.value]

        shared_features = [n for n, d in graph.nodes(data=True)
                         if d.get('is_shared', False)]
        distinguishing_features = [n for n, d in graph.nodes(data=True)
                                  if d.get('is_distinguishing', False)]

        return {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "concept_count": len(concept_nodes),
            "feature_count": len(feature_nodes),
            "shared_feature_count": len(shared_features),
            "distinguishing_feature_count": len(distinguishing_features),
            "avg_features_per_concept": len(feature_nodes) / max(len(concept_nodes), 1),
            "graph_density": nx.density(graph) if graph.number_of_nodes() > 0 else 0
        }

    def save_kg_data(self, output_path: str):
        """
        Save KG data to JSON file.

        Args:
            output_path: Path to save JSON file
        """
        data = {
            "concepts": {
                k: {
                    "name": v.name,
                    "category": v.category,
                    "appearances": v.appearances,
                    "wins": v.wins,
                    "win_rate": v.win_rate,
                    "features": v.features[:100],  # Limit for size
                    "statement_count": len(v.statements)
                }
                for k, v in self.kg_data.concepts.items()
            },
            "features": {
                k: {
                    "name": v.name,
                    "feature_type": v.feature_type,
                    "frequency": v.frequency,
                    "avg_relevance": v.avg_relevance,
                    "concepts": v.concepts,
                    "is_shared": v.is_shared,
                    "is_distinguishing": v.is_distinguishing
                }
                for k, v in self.kg_data.features.items()
            },
            "statistics": {
                "total_concepts": len(self.kg_data.concepts),
                "total_features": len(self.kg_data.features),
                "total_games": len(self.game_records)
            }
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse
    import gc

    parser = argparse.ArgumentParser(description="Build knowledge graph from game logs")
    parser.add_argument("--logs_dir", type=str, required=True,
                       help="Path to game logs directory")
    parser.add_argument("--output", type=str, default="icml_exp/KG/output/",
                       help="Output directory")
    parser.add_argument("--max_files", type=int, default=None,
                       help="Maximum number of log files to process")
    parser.add_argument("--category", type=str, default=None,
                       help="Filter by category")
    parser.add_argument("--language", type=str, default="en",
                       help="Language code")
    parser.add_argument("--no-nlp", action="store_true",
                       help="Disable spaCy NLP, use lightweight keyword extraction")
    parser.add_argument("--batch-size", type=int, default=0,
                       help="Process files in batches (0=no batching)")
    parser.add_argument("--min-freq", type=int, default=2,
                       help="Minimum feature frequency (default: 2)")
    parser.add_argument("--relevance-threshold", type=float, default=0.3,
                       help="Minimum relevance score (default: 0.3)")

    args = parser.parse_args()

    # Build KG
    builder = KnowledgeGraphBuilder(
        language=args.language,
        use_nlp=not args.no_nlp,
        min_feature_frequency=args.min_freq,
        relevance_threshold=args.relevance_threshold,
        merge_similar=True
    )

    log_path = Path(args.logs_dir)

    if args.batch_size > 0:
        # Batch processing mode
        json_files = list(log_path.rglob("*.json"))
        if args.category:
            json_files = [f for f in json_files if args.category in str(f)]
        if args.max_files:
            json_files = json_files[:args.max_files]

        total_files = len(json_files)
        print(f"Found {total_files} files, processing in batches of {args.batch_size}...")

        # Process in batches
        for batch_start in range(0, total_files, args.batch_size):
            batch_end = min(batch_start + args.batch_size, total_files)
            batch_files = json_files[batch_start:batch_end]

            print(f"\nProcessing batch {batch_start//args.batch_size + 1}: files {batch_start+1}-{batch_end}")

            # Load and process batch
            for file_path in batch_files:
                record = builder._load_single_log(file_path)
                if record:
                    builder.game_records.append(record)
                    builder._process_game_record(record)

            # Clear processed records to save memory
            gc.collect()

        # Merge similar features after all batches
        if builder.merge_similar:
            print("\nMerging similar features...")
            builder._merge_similar_features()

        # Build final graph
        graph = builder._build_networkx_graph()
    else:
        # Original single-pass mode
        print(f"Loading logs from {args.logs_dir}...")
        graph = builder.build_from_logs(
            args.logs_dir,
            max_files=args.max_files,
            category_filter=args.category
        )

    # Print statistics
    stats = builder.get_graph_statistics(graph)
    print("\n=== Knowledge Graph Statistics ===")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Save data
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = output_dir / "kg_data.json"
    builder.save_kg_data(str(data_path))
    print(f"\nKG data saved to {data_path}")
