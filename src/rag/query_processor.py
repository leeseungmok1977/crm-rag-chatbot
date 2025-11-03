"""
Query Preprocessor - Language detection and query optimization
"""

from typing import Literal
from langdetect import detect, LangDetectException


class QueryProcessor:
    """Process and optimize user queries"""

    def __init__(self):
        """Initialize query processor"""
        pass

    def detect_language(self, text: str) -> Literal["korean", "english"]:
        """
        Detect language of query text

        Args:
            text: Query text

        Returns:
            "korean" or "english"
        """
        try:
            detected = detect(text)
            return "korean" if detected == "ko" else "english"
        except LangDetectException:
            # Default to Korean for CRM context
            return "korean"

    def get_language_code(self, language: str) -> str:
        """
        Convert language name to code

        Args:
            language: "korean" or "english"

        Returns:
            "ko" or "en"
        """
        return "ko" if language == "korean" else "en"

    def optimize_query(self, query: str) -> str:
        """
        Optimize query for better search results

        Args:
            query: Original query

        Returns:
            Optimized query
        """
        # Remove extra whitespace
        query = " ".join(query.split())

        # Remove special characters that don't help search
        query = query.replace("?", "").replace("!", "")

        return query.strip()

    def extract_keywords(self, query: str, language: str) -> list[str]:
        """
        Extract keywords from query (simple implementation)

        Args:
            query: Query text
            language: Language of query

        Returns:
            List of keywords
        """
        # Simple keyword extraction by splitting
        # In production, use spaCy or similar NLP tools
        words = query.split()

        # Filter out common stop words
        if language == "korean":
            stop_words = {"은", "는", "이", "가", "을", "를", "의", "에", "에서",
                         "으로", "로", "과", "와", "하는", "하다", "있다"}
        else:
            stop_words = {"the", "a", "an", "in", "on", "at", "to", "for",
                         "of", "with", "is", "are", "how", "what", "when"}

        keywords = [w for w in words if w.lower() not in stop_words]
        return keywords
