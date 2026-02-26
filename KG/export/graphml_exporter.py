"""
GraphML format exporter for knowledge graphs.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: networkx not available. Install with: pip install networkx")

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import NodeType


class GraphMLExporter:
    """Export knowledge graphs to GraphML format."""

    def __init__(self):
        """Initialize the GraphML exporter."""
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx is required. Install with: pip install networkx")

    def export(
        self,
        graph: 'nx.Graph',
        output_path: str,
        include_positions: bool = False
    ) -> str:
        """
        Export NetworkX graph to GraphML format.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save output file
            include_positions: Whether to include node positions

        Returns:
            Path to the exported file
        """
        # Create a copy to avoid modifying the original
        export_graph = graph.copy()

        # Convert all attributes to GraphML-compatible types
        for node in export_graph.nodes():
            attrs = export_graph.nodes[node]
            for key, value in list(attrs.items()):
                # Convert non-string/number types to strings
                if isinstance(value, bool):
                    attrs[key] = str(value).lower()
                elif isinstance(value, (list, dict)):
                    attrs[key] = str(value)
                elif value is None:
                    attrs[key] = ""

        for u, v in export_graph.edges():
            attrs = export_graph.edges[u, v]
            for key, value in list(attrs.items()):
                if isinstance(value, bool):
                    attrs[key] = str(value).lower()
                elif isinstance(value, (list, dict)):
                    attrs[key] = str(value)
                elif value is None:
                    attrs[key] = ""

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Write GraphML
        nx.write_graphml(export_graph, output_path)

        return output_path

    def export_from_json(
        self,
        json_path: str,
        output_path: str
    ) -> str:
        """
        Export from JSON data file to GraphML.

        Args:
            json_path: Path to KG JSON data
            output_path: Path to save GraphML file

        Returns:
            Path to the exported file
        """
        import json

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        G = nx.Graph()

        # Add concept nodes
        for name, info in data.get('concepts', {}).items():
            G.add_node(
                name,
                node_type=NodeType.CONCEPT.value,
                category=info.get('category', ''),
                appearances=info.get('appearances', 0),
                wins=info.get('wins', 0),
                win_rate=info.get('win_rate', 0.0),
                label=name
            )

        # Add feature nodes and edges
        for name, info in data.get('features', {}).items():
            feature_name = info.get('name', name)

            G.add_node(
                feature_name,
                node_type=NodeType.FEATURE.value,
                feature_type=info.get('feature_type', ''),
                frequency=info.get('frequency', 1),
                avg_relevance=info.get('avg_relevance', 0.0),
                is_shared=str(info.get('is_shared', False)).lower(),
                is_distinguishing=str(info.get('is_distinguishing', False)).lower(),
                label=feature_name
            )

            # Add edges to concepts
            for concept in info.get('concepts', []):
                if concept in G.nodes():
                    G.add_edge(
                        concept,
                        feature_name,
                        weight=info.get('avg_relevance', 0.5),
                        edge_type="has_feature"
                    )

        return self.export(G, output_path)

    def import_graphml(self, input_path: str) -> 'nx.Graph':
        """
        Import a GraphML file into NetworkX graph.

        Args:
            input_path: Path to GraphML file

        Returns:
            NetworkX graph
        """
        return nx.read_graphml(input_path)


class GEXFExporter:
    """Export knowledge graphs to GEXF format (Gephi compatible)."""

    def __init__(self):
        """Initialize the GEXF exporter."""
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx is required")

    def export(
        self,
        graph: 'nx.Graph',
        output_path: str
    ) -> str:
        """
        Export NetworkX graph to GEXF format.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save output file

        Returns:
            Path to the exported file
        """
        # Create a copy to avoid modifying the original
        export_graph = graph.copy()

        # Convert attributes for GEXF compatibility
        for node in export_graph.nodes():
            attrs = export_graph.nodes[node]
            # Add viz attributes for Gephi
            if 'color' in attrs:
                color = attrs['color']
                if isinstance(color, str) and color.startswith('#'):
                    # Convert hex to RGB
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    attrs['viz'] = {'color': {'r': r, 'g': g, 'b': b}}

            if 'size' in attrs:
                if 'viz' not in attrs:
                    attrs['viz'] = {}
                attrs['viz']['size'] = attrs['size']

            # Convert non-compatible types
            for key, value in list(attrs.items()):
                if key == 'viz':
                    continue
                if isinstance(value, bool):
                    attrs[key] = str(value).lower()
                elif isinstance(value, (list, dict)):
                    attrs[key] = str(value)
                elif value is None:
                    del attrs[key]

        for u, v in export_graph.edges():
            attrs = export_graph.edges[u, v]
            for key, value in list(attrs.items()):
                if isinstance(value, bool):
                    attrs[key] = str(value).lower()
                elif isinstance(value, (list, dict)):
                    attrs[key] = str(value)
                elif value is None:
                    del attrs[key]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Write GEXF
        nx.write_gexf(export_graph, output_path)

        return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export knowledge graph to GraphML/GEXF")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to KG data JSON file")
    parser.add_argument("--output", type=str, default="icml_exp/KG/output/exports/kg.graphml",
                       help="Output file path")
    parser.add_argument("--format", type=str, default="graphml",
                       choices=["graphml", "gexf"],
                       help="Export format")

    args = parser.parse_args()

    if args.format == "graphml":
        exporter = GraphMLExporter()
    else:
        exporter = GEXFExporter()

    output = exporter.export_from_json(args.input, args.output)
    print(f"Graph exported to: {output}")
