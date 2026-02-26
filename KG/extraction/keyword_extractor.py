"""
Keyword-based feature extraction without heavy NLP dependencies.
"""

import re
from typing import List, Dict, Set, Optional
from collections import Counter

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import Feature


class KeywordExtractor:
    """Extract keywords and phrases using pattern-based methods."""

    # Common stopwords for filtering
    STOPWORDS = {
        "en": {
            "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such", "no",
            "nor", "not", "only", "own", "same", "so", "than", "too", "very",
            "just", "and", "but", "if", "or", "because", "until", "while",
            "although", "though", "even", "also", "both", "either", "neither",
            "this", "that", "these", "those", "it", "its", "itself", "they",
            "them", "their", "theirs", "themselves", "what", "which", "who",
            "whom", "whose", "i", "me", "my", "myself", "we", "our", "ours",
            "ourselves", "you", "your", "yours", "yourself", "yourselves",
            "he", "him", "his", "himself", "she", "her", "hers", "herself",
            "thing", "things", "something", "anything", "everything", "nothing",
            "one", "ones", "kind", "type", "way", "lot", "bit", "many", "much"
        }
    }

    # Feature indicator patterns
    FEATURE_PATTERNS = {
        "physical": [
            r"\b(color|colour|shape|size|texture|surface|material)\b",
            r"\b(round|square|flat|long|short|big|small|large|tiny)\b",
            r"\b(soft|hard|smooth|rough|shiny|dull|bright|dark)\b",
            r"\b(red|blue|green|yellow|black|white|brown|orange|purple|pink)\b"
        ],
        "functional": [
            r"\b(used for|used to|can be used|helps to|serves to)\b",
            r"\b(function|purpose|role|use|utility)\b",
            r"\b(make|create|produce|generate|provide)\b"
        ],
        "locational": [
            r"\b(found in|located|lives in|grows in|common in)\b",
            r"\b(indoor|outdoor|inside|outside|home|garden|nature)\b",
            r"\b(country|city|forest|ocean|mountain|desert)\b"
        ],
        "categorical": [
            r"\b(type of|kind of|species of|category|class)\b",
            r"\b(animal|plant|tool|food|vehicle|building)\b"
        ]
    }

    def __init__(self, language: str = "en"):
        """
        Initialize the keyword extractor.

        Args:
            language: Language code for stopwords
        """
        self.language = language
        self.stopwords = self.STOPWORDS.get(language, self.STOPWORDS["en"])

    def extract_features(self, statement: str) -> List[Feature]:
        """
        Extract keywords and phrases from a statement.

        Args:
            statement: The text to analyze

        Returns:
            List of extracted Feature objects
        """
        features = []

        # Extract n-grams
        features.extend(self._extract_ngrams(statement))

        # Extract pattern-matched features
        features.extend(self._extract_pattern_features(statement))

        # Deduplicate
        seen = set()
        unique_features = []
        for f in features:
            key = f.text.lower()
            if key not in seen:
                seen.add(key)
                f.source_statement = statement
                unique_features.append(f)

        return unique_features

    def _extract_ngrams(self, text: str, n_range: tuple = (1, 3)) -> List[Feature]:
        """Extract n-grams from text."""
        features = []

        # Clean and tokenize
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()

        # Filter stopwords for unigrams
        content_words = [w for w in words if w not in self.stopwords and len(w) > 2]

        # Unigrams
        for word in content_words:
            if self._is_valid_word(word):
                features.append(Feature(
                    text=word,
                    feature_type="keyword",
                    pos_tags=["WORD"]
                ))

        # Bigrams and trigrams
        for n in range(2, n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = words[i:i+n]
                # At least one content word
                if any(w not in self.stopwords and len(w) > 2 for w in ngram):
                    text_ngram = " ".join(ngram)
                    if self._is_valid_phrase(text_ngram):
                        features.append(Feature(
                            text=text_ngram,
                            feature_type=f"{n}gram",
                            pos_tags=["NGRAM"]
                        ))

        return features

    def _extract_pattern_features(self, text: str) -> List[Feature]:
        """Extract features based on predefined patterns."""
        features = []
        text_lower = text.lower()

        for category, patterns in self.FEATURE_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    features.append(Feature(
                        text=match.group(),
                        feature_type=f"pattern_{category}",
                        pos_tags=[category.upper()]
                    ))

        return features

    def _is_valid_word(self, word: str) -> bool:
        """Check if a word is valid for extraction."""
        if len(word) < 3:
            return False
        if word.isdigit():
            return False
        if word in self.stopwords:
            return False
        return True

    def _is_valid_phrase(self, phrase: str) -> bool:
        """Check if a phrase is valid for extraction."""
        words = phrase.split()
        if len(words) < 2:
            return False
        # At least one meaningful word
        content_count = sum(1 for w in words if w not in self.stopwords and len(w) > 2)
        return content_count >= 1

    def extract_weighted_keywords(
        self,
        statements: List[str],
        weights: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Extract keywords with TF weighting from multiple statements.

        Args:
            statements: List of statements
            weights: Optional relevance weights for each statement

        Returns:
            Dictionary of keyword -> weighted frequency
        """
        if weights is None:
            weights = [1.0] * len(statements)

        keyword_scores = Counter()

        for statement, weight in zip(statements, weights):
            features = self.extract_features(statement)
            for feature in features:
                keyword_scores[feature.text.lower()] += weight

        return dict(keyword_scores)

    def get_top_keywords(
        self,
        statements: List[str],
        weights: Optional[List[float]] = None,
        top_k: int = 20
    ) -> List[tuple]:
        """
        Get top-k weighted keywords.

        Args:
            statements: List of statements
            weights: Optional relevance weights
            top_k: Number of keywords to return

        Returns:
            List of (keyword, score) tuples
        """
        scores = self.extract_weighted_keywords(statements, weights)
        sorted_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_k]


if __name__ == "__main__":
    # Test the extractor
    extractor = KeywordExtractor(language="en")

    test_statements = [
        "This creature has colorful wings and can fly gracefully.",
        "It is commonly found in gardens and feeds on nectar from flowers.",
        "The species undergoes metamorphosis during its life cycle.",
    ]

    print("=== Single Statement Extraction ===")
    for stmt in test_statements:
        features = extractor.extract_features(stmt)
        print(f"\nStatement: {stmt}")
        print(f"Features ({len(features)}):")
        for f in features[:10]:  # Show first 10
            print(f"  - {f.text} ({f.feature_type})")

    print("\n=== Weighted Keywords ===")
    weights = [0.9, 0.8, 0.7]  # Simulated relevance scores
    top_keywords = extractor.get_top_keywords(test_statements, weights, top_k=10)
    for kw, score in top_keywords:
        print(f"  {kw}: {score:.2f}")
