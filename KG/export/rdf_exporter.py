"""
RDF/Turtle format exporter for knowledge graphs.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from rdflib import URIRef as URIRefType

from urllib.parse import quote

try:
    from rdflib import Graph, Namespace, Literal, URIRef, BNode
    from rdflib.namespace import RDF, RDFS, XSD, OWL
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    URIRef = None  # Placeholder for type checking
    print("Warning: rdflib not available. Install with: pip install rdflib")

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import NodeType, EdgeType


class RDFExporter:
    """Export knowledge graphs to RDF/Turtle format."""

    # Namespace definitions
    BASE_URI = "http://knowledgeedge.org/"

    def __init__(self, base_uri: Optional[str] = None):
        """
        Initialize the RDF exporter.

        Args:
            base_uri: Base URI for the ontology
        """
        if not RDFLIB_AVAILABLE:
            raise ImportError("rdflib is required. Install with: pip install rdflib")

        self.base_uri = base_uri or self.BASE_URI

        # Define namespaces
        self.KE = Namespace(self.base_uri)
        self.SCHEMA = Namespace("http://schema.org/")

    def export(
        self,
        graph: 'nx.Graph',
        output_path: str,
        format: str = "turtle"
    ) -> str:
        """
        Export NetworkX graph to RDF format.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save output file
            format: RDF serialization format (turtle, xml, n3, nt)

        Returns:
            Path to the exported file
        """
        rdf_graph = Graph()

        # Bind namespaces
        rdf_graph.bind("ke", self.KE)
        rdf_graph.bind("schema", self.SCHEMA)

        # Define classes
        rdf_graph.add((self.KE.Concept, RDF.type, RDFS.Class))
        rdf_graph.add((self.KE.Concept, RDFS.label, Literal("Concept")))

        rdf_graph.add((self.KE.Feature, RDF.type, RDFS.Class))
        rdf_graph.add((self.KE.Feature, RDFS.label, Literal("Feature")))

        # Define properties
        rdf_graph.add((self.KE.hasFeature, RDF.type, RDF.Property))
        rdf_graph.add((self.KE.hasFeature, RDFS.domain, self.KE.Concept))
        rdf_graph.add((self.KE.hasFeature, RDFS.range, self.KE.Feature))

        rdf_graph.add((self.KE.sharedWith, RDF.type, RDF.Property))
        rdf_graph.add((self.KE.sharedWith, RDFS.domain, self.KE.Feature))
        rdf_graph.add((self.KE.sharedWith, RDFS.range, self.KE.Concept))

        # Add nodes
        for node, attrs in graph.nodes(data=True):
            node_uri = self._make_uri(node)
            node_type = attrs.get('node_type', NodeType.FEATURE.value)

            if node_type == NodeType.CONCEPT.value:
                rdf_graph.add((node_uri, RDF.type, self.KE.Concept))
                rdf_graph.add((node_uri, RDFS.label, Literal(node)))

                if 'category' in attrs and attrs['category']:
                    rdf_graph.add((node_uri, self.KE.category, Literal(attrs['category'])))

                if 'appearances' in attrs:
                    rdf_graph.add((node_uri, self.KE.appearances,
                                  Literal(attrs['appearances'], datatype=XSD.integer)))

                if 'wins' in attrs:
                    rdf_graph.add((node_uri, self.KE.wins,
                                  Literal(attrs['wins'], datatype=XSD.integer)))

                if 'win_rate' in attrs:
                    rdf_graph.add((node_uri, self.KE.winRate,
                                  Literal(attrs['win_rate'], datatype=XSD.float)))

            elif node_type == NodeType.FEATURE.value:
                rdf_graph.add((node_uri, RDF.type, self.KE.Feature))
                rdf_graph.add((node_uri, RDFS.label, Literal(node)))

                if 'feature_type' in attrs:
                    rdf_graph.add((node_uri, self.KE.featureType,
                                  Literal(attrs['feature_type'])))

                if 'frequency' in attrs:
                    rdf_graph.add((node_uri, self.KE.frequency,
                                  Literal(attrs['frequency'], datatype=XSD.integer)))

                if 'avg_relevance' in attrs:
                    rdf_graph.add((node_uri, self.KE.avgRelevance,
                                  Literal(attrs['avg_relevance'], datatype=XSD.float)))

                if attrs.get('is_shared'):
                    rdf_graph.add((node_uri, self.KE.isShared,
                                  Literal(True, datatype=XSD.boolean)))

                if attrs.get('is_distinguishing'):
                    rdf_graph.add((node_uri, self.KE.isDistinguishing,
                                  Literal(True, datatype=XSD.boolean)))

        # Add edges
        for u, v, attrs in graph.edges(data=True):
            u_uri = self._make_uri(u)
            v_uri = self._make_uri(v)

            edge_type = attrs.get('edge_type', EdgeType.HAS_FEATURE.value)
            weight = attrs.get('weight', 1.0)

            # Create relationship
            if edge_type == EdgeType.HAS_FEATURE.value:
                rdf_graph.add((u_uri, self.KE.hasFeature, v_uri))
            else:
                rdf_graph.add((u_uri, self.KE.relatedTo, v_uri))

            # Add weight as reified statement (optional)
            if weight != 1.0:
                stmt = BNode()
                rdf_graph.add((stmt, RDF.type, RDF.Statement))
                rdf_graph.add((stmt, RDF.subject, u_uri))
                rdf_graph.add((stmt, RDF.predicate, self.KE.hasFeature))
                rdf_graph.add((stmt, RDF.object, v_uri))
                rdf_graph.add((stmt, self.KE.weight,
                              Literal(weight, datatype=XSD.float)))

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        # Serialize
        rdf_graph.serialize(destination=output_path, format=format)

        return output_path

    def _make_uri(self, text: str):
        """Create a valid URI from text."""
        # URL-encode the text
        safe_text = quote(str(text).replace(" ", "_"), safe="")
        return URIRef(self.KE[safe_text])

    def export_from_json(
        self,
        json_path: str,
        output_path: str,
        format: str = "turtle"
    ) -> str:
        """
        Export from JSON data file to RDF.

        Args:
            json_path: Path to KG JSON data
            output_path: Path to save RDF file
            format: RDF serialization format

        Returns:
            Path to the exported file
        """
        import json

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rdf_graph = Graph()
        rdf_graph.bind("ke", self.KE)

        # Add concepts
        for name, info in data.get('concepts', {}).items():
            uri = self._make_uri(name)
            rdf_graph.add((uri, RDF.type, self.KE.Concept))
            rdf_graph.add((uri, RDFS.label, Literal(name)))

            if info.get('category'):
                rdf_graph.add((uri, self.KE.category, Literal(info['category'])))
            if 'appearances' in info:
                rdf_graph.add((uri, self.KE.appearances,
                              Literal(info['appearances'], datatype=XSD.integer)))
            if 'wins' in info:
                rdf_graph.add((uri, self.KE.wins,
                              Literal(info['wins'], datatype=XSD.integer)))

        # Add features and relationships
        for name, info in data.get('features', {}).items():
            feature_name = info.get('name', name)
            uri = self._make_uri(feature_name)

            rdf_graph.add((uri, RDF.type, self.KE.Feature))
            rdf_graph.add((uri, RDFS.label, Literal(feature_name)))

            if info.get('feature_type'):
                rdf_graph.add((uri, self.KE.featureType, Literal(info['feature_type'])))
            if 'frequency' in info:
                rdf_graph.add((uri, self.KE.frequency,
                              Literal(info['frequency'], datatype=XSD.integer)))

            # Add relationships to concepts
            for concept in info.get('concepts', []):
                concept_uri = self._make_uri(concept)
                rdf_graph.add((concept_uri, self.KE.hasFeature, uri))

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        rdf_graph.serialize(destination=output_path, format=format)
        return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export knowledge graph to RDF")
    parser.add_argument("--input", type=str, required=True,
                       help="Path to KG data JSON file")
    parser.add_argument("--output", type=str, default="icml_exp/KG/output/exports/kg.ttl",
                       help="Output RDF file path")
    parser.add_argument("--format", type=str, default="turtle",
                       choices=["turtle", "xml", "n3", "nt"],
                       help="RDF serialization format")

    args = parser.parse_args()

    exporter = RDFExporter()
    output = exporter.export_from_json(args.input, args.output, format=args.format)
    print(f"RDF exported to: {output}")
