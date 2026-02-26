"""
JSON-LD format exporter for knowledge graphs.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import NodeType, EdgeType


class JSONLDExporter:
    """Export knowledge graphs to JSON-LD format."""

    # JSON-LD context
    CONTEXT = {
        "@vocab": "http://knowledgeedge.org/",
        "schema": "http://schema.org/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "Concept": "ke:Concept",
        "Feature": "ke:Feature",
        "name": "rdfs:label",
        "description": "schema:description",
        "category": "ke:category",
        "hasFeature": {
            "@id": "ke:hasFeature",
            "@type": "@id"
        },
        "sharedWith": {
            "@id": "ke:sharedWith",
            "@type": "@id"
        },
        "appearances": {
            "@id": "ke:appearances",
            "@type": "xsd:integer"
        },
        "wins": {
            "@id": "ke:wins",
            "@type": "xsd:integer"
        },
        "winRate": {
            "@id": "ke:winRate",
            "@type": "xsd:float"
        },
        "frequency": {
            "@id": "ke:frequency",
            "@type": "xsd:integer"
        },
        "avgRelevance": {
            "@id": "ke:avgRelevance",
            "@type": "xsd:float"
        },
        "featureType": "ke:featureType",
        "isShared": {
            "@id": "ke:isShared",
            "@type": "xsd:boolean"
        },
        "isDistinguishing": {
            "@id": "ke:isDistinguishing",
            "@type": "xsd:boolean"
        },
        "weight": {
            "@id": "ke:weight",
            "@type": "xsd:float"
        }
    }

    def __init__(self, base_uri: str = "http://knowledgeedge.org/"):
        """
        Initialize the JSON-LD exporter.

        Args:
            base_uri: Base URI for identifiers
        """
        self.base_uri = base_uri

    def export(
        self,
        graph: 'nx.Graph',
        output_path: str,
        include_context: bool = True,
        compact: bool = False
    ) -> str:
        """
        Export NetworkX graph to JSON-LD format.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save output file
            include_context: Whether to include @context
            compact: Whether to use compact output

        Returns:
            Path to the exported file
        """
        # Build the JSON-LD document
        doc = {}

        if include_context:
            doc["@context"] = self.CONTEXT

        # Build graph data
        graph_items = []

        # Process concept nodes
        concepts = []
        features = []

        for node, attrs in graph.nodes(data=True):
            node_type = attrs.get('node_type', NodeType.FEATURE.value)

            if node_type == NodeType.CONCEPT.value:
                concept_obj = self._build_concept_object(node, attrs, graph)
                concepts.append(concept_obj)
            elif node_type == NodeType.FEATURE.value:
                feature_obj = self._build_feature_object(node, attrs)
                features.append(feature_obj)

        # Add to document
        doc["@graph"] = concepts + features

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Write JSON
        indent = None if compact else 2
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=indent, ensure_ascii=False)

        return output_path

    def _build_concept_object(
        self,
        node: str,
        attrs: Dict[str, Any],
        graph: 'nx.Graph'
    ) -> Dict[str, Any]:
        """Build JSON-LD object for a concept node."""
        obj = {
            "@id": self._make_id(node),
            "@type": "Concept",
            "name": node
        }

        if 'category' in attrs and attrs['category']:
            obj["category"] = attrs['category']

        if 'appearances' in attrs:
            obj["appearances"] = attrs['appearances']

        if 'wins' in attrs:
            obj["wins"] = attrs['wins']

        if 'win_rate' in attrs:
            obj["winRate"] = round(attrs['win_rate'], 4)

        # Get connected features
        features = []
        for neighbor in graph.neighbors(node):
            neighbor_attrs = graph.nodes[neighbor]
            if neighbor_attrs.get('node_type') == NodeType.FEATURE.value:
                edge_data = graph.get_edge_data(node, neighbor) or {}
                features.append({
                    "@id": self._make_id(neighbor),
                    "weight": round(edge_data.get('weight', 1.0), 4)
                })

        if features:
            obj["hasFeature"] = features

        return obj

    def _build_feature_object(self, node: str, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON-LD object for a feature node."""
        obj = {
            "@id": self._make_id(node),
            "@type": "Feature",
            "name": node
        }

        if 'feature_type' in attrs:
            obj["featureType"] = attrs['feature_type']

        if 'frequency' in attrs:
            obj["frequency"] = attrs['frequency']

        if 'avg_relevance' in attrs:
            obj["avgRelevance"] = round(attrs['avg_relevance'], 4)

        if attrs.get('is_shared'):
            obj["isShared"] = True

        if attrs.get('is_distinguishing'):
            obj["isDistinguishing"] = True

        return obj

    def _make_id(self, text: str) -> str:
        """Create a valid JSON-LD ID from text."""
        safe_text = text.replace(" ", "_").replace("/", "_")
        return f"{self.base_uri}{safe_text}"

    def export_from_json(
        self,
        json_path: str,
        output_path: str,
        include_context: bool = True
    ) -> str:
        """
        Export from JSON data file to JSON-LD.

        Args:
            json_path: Path to KG JSON data
            output_path: Path to save JSON-LD file
            include_context: Whether to include @context

        Returns:
            Path to the exported file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        doc = {}
        if include_context:
            doc["@context"] = self.CONTEXT

        graph_items = []

        # Add concepts
        for name, info in data.get('concepts', {}).items():
            obj = {
                "@id": self._make_id(name),
                "@type": "Concept",
                "name": name
            }

            if info.get('category'):
                obj["category"] = info['category']
            if 'appearances' in info:
                obj["appearances"] = info['appearances']
            if 'wins' in info:
                obj["wins"] = info['wins']
            if 'win_rate' in info:
                obj["winRate"] = round(info['win_rate'], 4)

            # Features will be linked from feature objects
            graph_items.append(obj)

        # Add features
        for name, info in data.get('features', {}).items():
            feature_name = info.get('name', name)
            obj = {
                "@id": self._make_id(feature_name),
                "@type": "Feature",
                "name": feature_name
            }

            if info.get('feature_type'):
                obj["featureType"] = info['feature_type']
            if 'frequency' in info:
                obj["frequency"] = info['frequency']
            if 'avg_relevance' in info:
                obj["avgRelevance"] = round(info['avg_relevance'], 4)
            if info.get('is_shared'):
                obj["isShared"] = True
            if info.get('is_distinguishing'):
                obj["isDistinguishing"] = True

            # Link to concepts
            concepts = info.get('concepts', [])
            if concepts:
                obj["sharedWith"] = [self._make_id(c) for c in concepts]

            graph_items.append(obj)

        doc["@graph"] = graph_items

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

        return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export knowledge graph to JSON-LD")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to KG data JSON file")
    parser.add_argument("--output", type=str, default="icml_exp/KG/output/exports/kg.jsonld",
                       help="Output JSON-LD file path")
    parser.add_argument("--no-context", action="store_true",
                       help="Exclude @context from output")

    args = parser.parse_args()

    exporter = JSONLDExporter()
    output = exporter.export_from_json(
        args.input,
        args.output,
        include_context=not args.no_context
    )
    print(f"JSON-LD exported to: {output}")
