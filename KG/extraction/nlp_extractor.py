"""
NLP-based feature extraction using spaCy.
"""

import re
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from spacy.tokens import Doc

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")

import sys
sys.path.append(".")
from icml_exp.KG.builder.kg_schema import Feature


@dataclass
class ExtractionConfig:
    """Configuration for feature extraction."""
    extract_noun_phrases: bool = True
    extract_adj_noun: bool = True
    extract_verb_phrases: bool = True
    extract_entities: bool = True
    min_phrase_length: int = 2
    max_phrase_length: int = 50
    stopwords: List[str] = None

    def __post_init__(self):
        if self.stopwords is None:
            self.stopwords = [
                "it", "this", "that", "these", "those", "something",
                "thing", "stuff", "one", "ones", "kind", "type",
                "way", "lot", "bit", "many", "much", "some", "any"
            ]


class NLPFeatureExtractor:
    """Extract structured features from statements using spaCy NLP."""

    LANGUAGE_MODELS = {
        "en": "en_core_web_sm",
        "zh": "zh_core_web_sm",
        "de": "de_core_news_sm",
        "fr": "fr_core_news_sm",
        "es": "es_core_news_sm",
        "it": "it_core_news_sm",
        "pt": "pt_core_news_sm",
        "ja": "ja_core_news_sm",
        "ru": "ru_core_news_sm",
    }

    def __init__(self, language: str = "en", config: Optional[ExtractionConfig] = None):
        """
        Initialize the NLP extractor.

        Args:
            language: Language code (en, zh, de, fr, etc.)
            config: Extraction configuration
        """
        self.language = language
        self.config = config or ExtractionConfig()
        self.nlp = None

        if SPACY_AVAILABLE:
            self._load_model()

    def _load_model(self):
        """Load the appropriate spaCy model."""
        model_name = self.LANGUAGE_MODELS.get(self.language, "en_core_web_sm")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Model {model_name} not found. Downloading...")
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)

    def extract_features(self, statement: str) -> List[Feature]:
        """
        Extract all features from a statement.

        Args:
            statement: The text statement to analyze

        Returns:
            List of extracted Feature objects
        """
        if not SPACY_AVAILABLE or self.nlp is None:
            return self._fallback_extraction(statement)

        doc = self.nlp(statement)
        features = []

        if self.config.extract_noun_phrases:
            features.extend(self._extract_noun_phrases(doc))

        if self.config.extract_adj_noun:
            features.extend(self._extract_adj_noun_combinations(doc))

        if self.config.extract_verb_phrases:
            features.extend(self._extract_verb_phrases(doc))

        if self.config.extract_entities:
            features.extend(self._extract_entities(doc))

        # Deduplicate features
        seen = set()
        unique_features = []
        for f in features:
            key = f.text.lower()
            if key not in seen and self._is_valid_feature(f):
                seen.add(key)
                f.source_statement = statement
                unique_features.append(f)

        return unique_features

    def _extract_noun_phrases(self, doc: "Doc") -> List[Feature]:
        """Extract noun phrase chunks."""
        features = []
        for chunk in doc.noun_chunks:
            text = chunk.text.strip()
            if self._is_valid_phrase(text):
                features.append(Feature(
                    text=text,
                    feature_type="noun_phrase",
                    pos_tags=[token.pos_ for token in chunk]
                ))
        return features

    def _extract_adj_noun_combinations(self, doc: "Doc") -> List[Feature]:
        """Extract adjective-noun combinations."""
        features = []
        for token in doc:
            if token.pos_ == "NOUN":
                # Find adjective modifiers
                adj_modifiers = [
                    child for child in token.children
                    if child.pos_ == "ADJ" and child.dep_ in ("amod", "attr")
                ]
                for adj in adj_modifiers:
                    text = f"{adj.text} {token.text}"
                    if self._is_valid_phrase(text):
                        features.append(Feature(
                            text=text,
                            feature_type="adj_noun",
                            pos_tags=["ADJ", "NOUN"]
                        ))
        return features

    def _extract_verb_phrases(self, doc: "Doc") -> List[Feature]:
        """Extract verb phrases for functional descriptions."""
        features = []
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ in ("ROOT", "relcl", "advcl"):
                # Get the verb and its direct objects/complements
                phrase_parts = [token.text]
                for child in token.children:
                    if child.dep_ in ("dobj", "pobj", "attr", "acomp"):
                        phrase_parts.append(child.text)

                if len(phrase_parts) > 1:
                    text = " ".join(phrase_parts)
                    if self._is_valid_phrase(text):
                        features.append(Feature(
                            text=text,
                            feature_type="verb_phrase",
                            pos_tags=["VERB", "OBJ"]
                        ))
        return features

    def _extract_entities(self, doc: "Doc") -> List[Feature]:
        """Extract named entities."""
        features = []
        for ent in doc.ents:
            text = ent.text.strip()
            if self._is_valid_phrase(text):
                features.append(Feature(
                    text=text,
                    feature_type=f"entity_{ent.label_}",
                    pos_tags=[ent.label_]
                ))
        return features

    def _is_valid_phrase(self, text: str) -> bool:
        """Check if a phrase is valid for extraction."""
        text = text.strip()
        if len(text) < self.config.min_phrase_length:
            return False
        if len(text) > self.config.max_phrase_length:
            return False
        # Skip if it's just stopwords
        words = text.lower().split()
        if all(w in self.config.stopwords for w in words):
            return False
        return True

    def _is_valid_feature(self, feature: Feature) -> bool:
        """Additional validation for features."""
        text = feature.text.lower().strip()
        # Skip very short or very long features
        if len(text) < 2 or len(text) > 100:
            return False
        # Skip if only numbers or punctuation
        if re.match(r'^[\d\s\W]+$', text):
            return False
        return True

    def _fallback_extraction(self, statement: str) -> List[Feature]:
        """Fallback extraction when spaCy is not available."""
        features = []
        # Simple word-based extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', statement.lower())

        # Extract potential features (simple heuristics)
        for word in words:
            if word not in self.config.stopwords:
                features.append(Feature(
                    text=word,
                    feature_type="word",
                    pos_tags=["UNKNOWN"],
                    source_statement=statement
                ))

        return features

    def extract_batch(self, statements: List[str]) -> Dict[str, List[Feature]]:
        """
        Extract features from multiple statements efficiently.

        Args:
            statements: List of statements to process

        Returns:
            Dictionary mapping statements to their features
        """
        results = {}

        if SPACY_AVAILABLE and self.nlp is not None:
            # Use pipe for efficient batch processing
            docs = list(self.nlp.pipe(statements))
            for statement, doc in zip(statements, docs):
                features = []
                if self.config.extract_noun_phrases:
                    features.extend(self._extract_noun_phrases(doc))
                if self.config.extract_adj_noun:
                    features.extend(self._extract_adj_noun_combinations(doc))
                if self.config.extract_verb_phrases:
                    features.extend(self._extract_verb_phrases(doc))
                if self.config.extract_entities:
                    features.extend(self._extract_entities(doc))

                # Deduplicate
                seen = set()
                unique = []
                for f in features:
                    key = f.text.lower()
                    if key not in seen and self._is_valid_feature(f):
                        seen.add(key)
                        f.source_statement = statement
                        unique.append(f)
                results[statement] = unique
        else:
            for statement in statements:
                results[statement] = self._fallback_extraction(statement)

        return results


if __name__ == "__main__":
    # Test the extractor
    extractor = NLPFeatureExtractor(language="en")

    test_statements = [
        "This creature has colorful wings and can fly gracefully.",
        "It is commonly found in gardens and feeds on nectar from flowers.",
        "The species undergoes metamorphosis during its life cycle.",
    ]

    for stmt in test_statements:
        features = extractor.extract_features(stmt)
        print(f"\nStatement: {stmt}")
        print(f"Features ({len(features)}):")
        for f in features:
            print(f"  - {f.text} ({f.feature_type})")
