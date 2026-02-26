"""
Data model definitions for Knowledge Graph construction.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    CONCEPT = "concept"
    FEATURE = "feature"
    CATEGORY = "category"


class EdgeType(Enum):
    """Types of edges in the knowledge graph."""
    HAS_FEATURE = "has_feature"
    SHARED_BY = "shared_by"
    DISTINGUISHES = "distinguishes"
    BELONGS_TO = "belongs_to"


@dataclass
class Feature:
    """Represents an extracted feature from a statement."""
    text: str
    feature_type: str  # noun_phrase, adj_noun, verb_phrase, entity
    pos_tags: List[str] = field(default_factory=list)
    source_statement: Optional[str] = None
    confidence: float = 1.0

    def __hash__(self):
        return hash(self.text.lower())

    def __eq__(self, other):
        if isinstance(other, Feature):
            return self.text.lower() == other.text.lower()
        return False


@dataclass
class ConceptNode:
    """Represents a concept in the knowledge graph."""
    name: str
    node_type: NodeType = NodeType.CONCEPT
    category: Optional[str] = None
    appearances: int = 0
    wins: int = 0
    features: List[str] = field(default_factory=list)
    statements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def win_rate(self) -> float:
        """Calculate win rate for this concept."""
        if self.appearances == 0:
            return 0.0
        return self.wins / self.appearances


@dataclass
class FeatureNode:
    """Represents a feature in the knowledge graph."""
    name: str
    node_type: NodeType = NodeType.FEATURE
    feature_type: str = "unknown"
    frequency: int = 1
    avg_relevance: float = 0.0
    concepts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_shared(self) -> bool:
        """Check if feature is shared by multiple concepts."""
        return len(self.concepts) > 1

    @property
    def is_distinguishing(self) -> bool:
        """Check if feature distinguishes a single concept."""
        return len(self.concepts) == 1


@dataclass
class Edge:
    """Represents an edge in the knowledge graph."""
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatementRecord:
    """Represents a statement with its evaluation metrics."""
    statement_id: int
    player_id: int
    llm_id: str
    content: str
    statement_round: int
    assigned_concept: str
    role: str  # civilian or undercover
    novelty_score: float = 0.0
    relevance_score: float = 0.0
    reasonableness_score: float = 0.0

    @property
    def quality_score(self) -> float:
        """Calculate overall quality score."""
        return (self.novelty_score + self.relevance_score + self.reasonableness_score) / 3


@dataclass
class GameRecord:
    """Parsed game record for KG construction."""
    game_id: str
    category: str
    concept_a: str
    concept_b: str
    winner_role: str
    statements: List[StatementRecord] = field(default_factory=list)

    @property
    def concept_a_won(self) -> bool:
        """Check if concept_a side won."""
        return self.winner_role == "civilian"


@dataclass
class KnowledgeGraphData:
    """Complete knowledge graph data structure."""
    concepts: Dict[str, ConceptNode] = field(default_factory=dict)
    features: Dict[str, FeatureNode] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_concept(self, concept: ConceptNode):
        """Add or update a concept node."""
        if concept.name in self.concepts:
            existing = self.concepts[concept.name]
            existing.appearances += concept.appearances
            existing.wins += concept.wins
            existing.features.extend(concept.features)
            existing.statements.extend(concept.statements)
        else:
            self.concepts[concept.name] = concept

    def add_feature(self, feature: FeatureNode):
        """Add or update a feature node."""
        if feature.name in self.features:
            existing = self.features[feature.name]
            existing.frequency += feature.frequency
            for c in feature.concepts:
                if c not in existing.concepts:
                    existing.concepts.append(c)
        else:
            self.features[feature.name] = feature

    def add_edge(self, edge: Edge):
        """Add an edge to the graph."""
        self.edges.append(edge)

    def get_concept_features(self, concept_name: str) -> List[FeatureNode]:
        """Get all features associated with a concept."""
        return [f for f in self.features.values() if concept_name in f.concepts]

    def get_shared_features(self) -> List[FeatureNode]:
        """Get features shared by multiple concepts."""
        return [f for f in self.features.values() if f.is_shared]

    def get_distinguishing_features(self, concept_name: str) -> List[FeatureNode]:
        """Get features that distinguish a specific concept."""
        return [f for f in self.features.values()
                if f.is_distinguishing and concept_name in f.concepts]
