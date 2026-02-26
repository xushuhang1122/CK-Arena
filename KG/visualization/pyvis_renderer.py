"""
Interactive knowledge graph visualization using pyvis.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from pyvis.network import Network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False
    print("Warning: pyvis not available. Install with: pip install pyvis")

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import NodeType


class PyvisRenderer:
    """Render knowledge graphs as interactive HTML using pyvis."""

    # Default visual settings
    DEFAULT_SETTINGS = {
        "height": "800px",
        "width": "100%",
        "bgcolor": "#ffffff",
        "font_color": "#333333",
        "heading": ""
    }

    # Node type configurations
    NODE_CONFIGS = {
        NodeType.CONCEPT.value: {
            "shape": "ellipse",
            "font_size": 20,
            "border_width": 3
        },
        NodeType.FEATURE.value: {
            "shape": "dot",
            "font_size": 12,
            "border_width": 1
        },
        NodeType.CATEGORY.value: {
            "shape": "box",
            "font_size": 16,
            "border_width": 2
        }
    }

    def __init__(
        self,
        height: str = "800px",
        width: str = "100%",
        bgcolor: str = "#ffffff",
        directed: bool = False
    ):
        """
        Initialize the renderer.

        Args:
            height: Canvas height (CSS value)
            width: Canvas width (CSS value)
            bgcolor: Background color
            directed: Whether to show directed edges
        """
        if not PYVIS_AVAILABLE:
            raise ImportError("pyvis is required. Install with: pip install pyvis")

        self.height = height
        self.width = width
        self.bgcolor = bgcolor
        self.directed = directed

    def render(
        self,
        graph: 'nx.Graph',
        output_path: str,
        title: str = "Knowledge Graph",
        physics_enabled: bool = True,
        show_buttons: bool = True
    ) -> str:
        """
        Render a NetworkX graph to an interactive HTML file.

        Args:
            graph: NetworkX graph to render
            output_path: Path to save HTML file
            title: Title displayed on the page
            physics_enabled: Whether to enable physics simulation
            show_buttons: Whether to show control buttons

        Returns:
            Path to the generated HTML file
        """
        # Create pyvis network
        net = Network(
            height=self.height,
            width=self.width,
            bgcolor=self.bgcolor,
            font_color="#333333",
            directed=self.directed,
            heading=title
        )

        # Configure physics
        if physics_enabled:
            net.barnes_hut(
                gravity=-80000,
                central_gravity=0.3,
                spring_length=200,
                spring_strength=0.001,
                damping=0.09
            )
        else:
            net.toggle_physics(False)

        # Add nodes
        for node, attrs in graph.nodes(data=True):
            node_type = attrs.get('node_type', NodeType.FEATURE.value)
            config = self.NODE_CONFIGS.get(node_type, self.NODE_CONFIGS[NodeType.FEATURE.value])

            # Build tooltip
            tooltip = self._build_tooltip(node, attrs)

            net.add_node(
                node,
                label=str(node),
                title=tooltip,
                color=attrs.get('color', '#97c2fc'),
                size=attrs.get('size', 25),
                shape=config['shape'],
                font={'size': config['font_size']},
                borderWidth=config['border_width']
            )

        # Add edges
        for u, v, attrs in graph.edges(data=True):
            weight = attrs.get('weight', 1.0)
            edge_type = attrs.get('edge_type', 'related')

            net.add_edge(
                u, v,
                width=max(1, weight * 2),
                title=f"{edge_type}: {weight:.2f}",
                color={'opacity': min(0.3 + weight * 0.5, 1.0)}
            )

        # Enable interaction buttons
        if show_buttons:
            net.show_buttons(filter_=['physics', 'nodes', 'edges'])

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Save graph
        net.save_graph(output_path)

        return output_path

    def _build_tooltip(self, node: str, attrs: Dict[str, Any]) -> str:
        """Build HTML tooltip for a node."""
        node_type = attrs.get('node_type', 'unknown')
        lines = [f"<b>{node}</b>", f"Type: {node_type}"]

        if node_type == NodeType.CONCEPT.value:
            if 'category' in attrs:
                lines.append(f"Category: {attrs['category']}")
            if 'appearances' in attrs:
                lines.append(f"Games: {attrs['appearances']}")
            if 'wins' in attrs:
                lines.append(f"Wins: {attrs['wins']}")
            if 'win_rate' in attrs:
                lines.append(f"Win rate: {attrs['win_rate']:.1%}")

        elif node_type == NodeType.FEATURE.value:
            if 'feature_type' in attrs:
                lines.append(f"Feature type: {attrs['feature_type']}")
            if 'frequency' in attrs:
                lines.append(f"Frequency: {attrs['frequency']}")
            if 'avg_relevance' in attrs:
                lines.append(f"Avg relevance: {attrs['avg_relevance']:.2f}")
            if attrs.get('is_shared'):
                lines.append("<i>Shared feature</i>")
            if attrs.get('is_distinguishing'):
                lines.append("<i>Distinguishing feature</i>")

        return "<br>".join(lines)

    def render_concept_pair(
        self,
        graph: 'nx.Graph',
        concept_a: str,
        concept_b: str,
        output_path: str,
        max_features: int = 50
    ) -> str:
        """
        Render a focused view of a concept pair.

        Args:
            graph: Full knowledge graph
            concept_a: First concept
            concept_b: Second concept
            output_path: Path to save HTML
            max_features: Maximum features to show per concept

        Returns:
            Path to generated HTML
        """
        # Create subgraph for this pair
        relevant_nodes = {concept_a, concept_b}

        # Get features for each concept
        for concept in [concept_a, concept_b]:
            if concept in graph:
                neighbors = list(graph.neighbors(concept))
                # Sort by relevance/weight and take top N
                weighted_neighbors = []
                for n in neighbors:
                    edge_data = graph.get_edge_data(concept, n) or {}
                    weight = edge_data.get('weight', 0)
                    weighted_neighbors.append((n, weight))
                weighted_neighbors.sort(key=lambda x: x[1], reverse=True)
                relevant_nodes.update([n for n, _ in weighted_neighbors[:max_features]])

        subgraph = graph.subgraph(relevant_nodes).copy()

        # Color nodes by which concept they belong to
        concept_a_features = set(graph.neighbors(concept_a)) if concept_a in graph else set()
        concept_b_features = set(graph.neighbors(concept_b)) if concept_b in graph else set()

        for node in subgraph.nodes():
            if node == concept_a:
                subgraph.nodes[node]['color'] = '#2E8B57'  # Sea green
            elif node == concept_b:
                subgraph.nodes[node]['color'] = '#FFD700'  # Gold
            elif node in concept_a_features and node in concept_b_features:
                subgraph.nodes[node]['color'] = '#87CEEB'  # Sky blue (shared)
            elif node in concept_a_features:
                subgraph.nodes[node]['color'] = '#98FB98'  # Pale green
            elif node in concept_b_features:
                subgraph.nodes[node]['color'] = '#F0E68C'  # Khaki

        title = f"Knowledge Graph: {concept_a} vs {concept_b}"
        return self.render(subgraph, output_path, title=title)

    def render_from_json(
        self,
        json_path: str,
        output_path: str,
        title: str = "Knowledge Graph"
    ) -> str:
        """
        Render a graph from saved JSON data.

        Args:
            json_path: Path to KG JSON data
            output_path: Path to save HTML
            title: Title for the visualization

        Returns:
            Path to generated HTML
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx is required")

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
                win_rate=info.get('win_rate', 0),
                color='#2E8B57',
                size=40
            )

        # Add feature nodes and edges
        for name, info in data.get('features', {}).items():
            is_shared = info.get('is_shared', False)
            color = '#87CEEB' if is_shared else '#98FB98'

            G.add_node(
                info.get('name', name),
                node_type=NodeType.FEATURE.value,
                feature_type=info.get('feature_type', ''),
                frequency=info.get('frequency', 1),
                avg_relevance=info.get('avg_relevance', 0),
                is_shared=is_shared,
                is_distinguishing=info.get('is_distinguishing', False),
                color=color,
                size=15 + min(info.get('frequency', 1) * 2, 25)
            )

            # Add edges
            for concept in info.get('concepts', []):
                if concept in G.nodes():
                    G.add_edge(
                        concept,
                        info.get('name', name),
                        weight=info.get('avg_relevance', 0.5)
                    )

        return self.render(G, output_path, title=title)


class LegendGenerator:
    """Generate legend HTML for the visualization."""

    @staticmethod
    def generate_legend_html(
        colors: Dict[str, str],
        title: str = "Legend"
    ) -> str:
        """Generate HTML legend."""
        items = []
        for label, color in colors.items():
            items.append(
                f'<div style="display:flex;align-items:center;margin:5px 0;">'
                f'<div style="width:20px;height:20px;background:{color};'
                f'border-radius:50%;margin-right:10px;"></div>'
                f'<span>{label}</span></div>'
            )

        return f"""
        <div style="position:fixed;top:10px;right:10px;background:white;
                    padding:15px;border-radius:5px;box-shadow:0 2px 5px rgba(0,0,0,0.2);
                    font-family:Arial,sans-serif;z-index:1000;">
            <h3 style="margin:0 0 10px 0;">{title}</h3>
            {''.join(items)}
        </div>
        """


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render knowledge graph visualization")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to KG data JSON file")
    parser.add_argument("--output", type=str, default="icml_exp/KG/output/graphs/kg.html",
                       help="Output HTML path")
    parser.add_argument("--title", type=str, default="Knowledge Graph",
                       help="Visualization title")

    args = parser.parse_args()

    renderer = PyvisRenderer()
    output = renderer.render_from_json(args.input, args.output, title=args.title)
    print(f"Visualization saved to: {output}")
