"""
Feature merging using semantic similarity clustering.
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import AgglomerativeClustering
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using simple merging.")

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import Feature, FeatureNode


class FeatureMerger:
    """Merge similar features using semantic clustering."""

    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize the feature merger.

        Args:
            similarity_threshold: Threshold for considering features similar (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = None
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                analyzer='char_wb',
                ngram_range=(2, 4),
                min_df=1
            )

    def merge_features(
        self,
        features: List[Feature],
        weights: Optional[Dict[str, float]] = None
    ) -> List[FeatureNode]:
        """
        Merge similar features into unified feature nodes.

        Args:
            features: List of Feature objects to merge
            weights: Optional weights for each feature text

        Returns:
            List of merged FeatureNode objects
        """
        if not features:
            return []

        if weights is None:
            weights = {}

        if SKLEARN_AVAILABLE and len(features) > 1:
            return self._cluster_based_merge(features, weights)
        else:
            return self._simple_merge(features, weights)

    def _cluster_based_merge(
        self,
        features: List[Feature],
        weights: Dict[str, float]
    ) -> List[FeatureNode]:
        """Merge features using clustering."""
        # Extract unique feature texts
        feature_texts = list(set(f.text.lower() for f in features))

        if len(feature_texts) < 2:
            return self._simple_merge(features, weights)

        # Compute TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(feature_texts)

            # Compute similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Convert to distance matrix
            distance_matrix = 1 - similarity_matrix
            np.fill_diagonal(distance_matrix, 0)

            # Cluster similar features
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=1 - self.similarity_threshold,
                metric='precomputed',
                linkage='average'
            )
            cluster_labels = clustering.fit_predict(distance_matrix)

            # Group features by cluster
            clusters = defaultdict(list)
            for text, label in zip(feature_texts, cluster_labels):
                clusters[label].append(text)

            # Create merged nodes
            merged_nodes = []
            for cluster_id, texts in clusters.items():
                # Select representative (most frequent or highest weighted)
                representative = max(
                    texts,
                    key=lambda t: weights.get(t, 1.0)
                )

                # Aggregate info from all features in cluster
                feature_types = set()
                concepts = set()
                total_weight = 0

                for f in features:
                    if f.text.lower() in texts:
                        feature_types.add(f.feature_type)
                        total_weight += weights.get(f.text.lower(), 1.0)

                node = FeatureNode(
                    name=representative,
                    feature_type=list(feature_types)[0] if feature_types else "merged",
                    frequency=len(texts),
                    avg_relevance=total_weight / len(texts) if texts else 0,
                    concepts=list(concepts),
                    metadata={
                        "variants": texts,
                        "cluster_size": len(texts)
                    }
                )
                merged_nodes.append(node)

            return merged_nodes

        except Exception as e:
            print(f"Clustering failed: {e}. Using simple merge.")
            return self._simple_merge(features, weights)

    def _simple_merge(
        self,
        features: List[Feature],
        weights: Dict[str, float]
    ) -> List[FeatureNode]:
        """Simple merging based on exact/substring matching."""
        # Group by normalized text
        groups = defaultdict(list)
        for f in features:
            normalized = self._normalize_text(f.text)
            groups[normalized].append(f)

        # Create nodes
        nodes = []
        for normalized, group in groups.items():
            # Select representative
            representative = max(
                group,
                key=lambda f: weights.get(f.text.lower(), 1.0)
            )

            feature_types = set(f.feature_type for f in group)
            total_weight = sum(weights.get(f.text.lower(), 1.0) for f in group)

            node = FeatureNode(
                name=representative.text,
                feature_type=list(feature_types)[0] if feature_types else "merged",
                frequency=len(group),
                avg_relevance=total_weight / len(group) if group else 0,
                concepts=[],
                metadata={
                    "variants": [f.text for f in group],
                    "cluster_size": len(group)
                }
            )
            nodes.append(node)

        return nodes

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def find_similar_pairs(
        self,
        features: List[str]
    ) -> List[Tuple[str, str, float]]:
        """
        Find pairs of similar features.

        Args:
            features: List of feature strings

        Returns:
            List of (feature1, feature2, similarity) tuples
        """
        if not SKLEARN_AVAILABLE or len(features) < 2:
            return []

        try:
            tfidf_matrix = self.vectorizer.fit_transform(features)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            pairs = []
            for i in range(len(features)):
                for j in range(i + 1, len(features)):
                    sim = similarity_matrix[i, j]
                    if sim >= self.similarity_threshold:
                        pairs.append((features[i], features[j], sim))

            return sorted(pairs, key=lambda x: x[2], reverse=True)

        except Exception:
            return []

    def merge_concept_features(
        self,
        concept_features: Dict[str, List[Feature]],
        weights: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Dict[str, List[FeatureNode]]:
        """
        Merge features for multiple concepts.

        Args:
            concept_features: Dict mapping concept names to their features
            weights: Optional nested dict of concept -> feature -> weight

        Returns:
            Dict mapping concept names to merged FeatureNodes
        """
        if weights is None:
            weights = {}

        result = {}
        for concept, features in concept_features.items():
            concept_weights = weights.get(concept, {})
            merged = self.merge_features(features, concept_weights)

            # Add concept info to nodes
            for node in merged:
                if concept not in node.concepts:
                    node.concepts.append(concept)

            result[concept] = merged

        return result


if __name__ == "__main__":
    # Test the merger
    merger = FeatureMerger(similarity_threshold=0.6)

    test_features = [
        Feature(text="colorful wings", feature_type="adj_noun"),
        Feature(text="colourful wing", feature_type="adj_noun"),
        Feature(text="colored wings", feature_type="adj_noun"),
        Feature(text="nectar from flowers", feature_type="noun_phrase"),
        Feature(text="flower nectar", feature_type="noun_phrase"),
        Feature(text="metamorphosis", feature_type="keyword"),
        Feature(text="life cycle", feature_type="noun_phrase"),
    ]

    weights = {
        "colorful wings": 0.9,
        "colourful wing": 0.85,
        "colored wings": 0.8,
        "nectar from flowers": 0.7,
        "flower nectar": 0.75,
        "metamorphosis": 0.95,
        "life cycle": 0.6
    }

    print("=== Feature Merging Test ===")
    merged = merger.merge_features(test_features, weights)

    for node in merged:
        print(f"\n{node.name}:")
        print(f"  Type: {node.feature_type}")
        print(f"  Frequency: {node.frequency}")
        print(f"  Avg relevance: {node.avg_relevance:.2f}")
        print(f"  Variants: {node.metadata.get('variants', [])}")
