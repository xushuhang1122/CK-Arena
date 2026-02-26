"""
Knowledge Graph module for KnowledgeEdge project.

This module provides tools for:
- Building knowledge graphs from game logs
- NLP-based feature extraction
- Interactive visualization with pyvis
- Standard format export (RDF, JSON-LD, GraphML)
- Pure collection mode games for data gathering
"""

from icml_exp.KG.builder.kg_schema import (
    NodeType,
    EdgeType,
    Feature,
    ConceptNode,
    FeatureNode,
    Edge,
    StatementRecord,
    GameRecord,
    KnowledgeGraphData
)

from icml_exp.KG.builder.kg_builder import KnowledgeGraphBuilder

__version__ = "1.0.0"

__all__ = [
    # Schema
    "NodeType",
    "EdgeType",
    "Feature",
    "ConceptNode",
    "FeatureNode",
    "Edge",
    "StatementRecord",
    "GameRecord",
    "KnowledgeGraphData",
    # Builder
    "KnowledgeGraphBuilder",
]
