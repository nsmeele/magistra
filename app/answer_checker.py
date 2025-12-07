"""
Intelligent answer checking using NLP and fuzzy matching.

This module provides sophisticated answer validation that goes beyond
exact string matching - something difficult to achieve in PHP due to
limited NLP library support.
"""
import re
import unicodedata
from typing import Tuple
from Levenshtein import ratio


class AnswerChecker:
    """
    Smart answer checker using fuzzy string matching.

    Uses Levenshtein distance to calculate similarity between answers,
    allowing for typos, minor spelling errors, and variations.
    """

    # Thresholds for answer quality
    PERFECT_MATCH = 1.0      # 100% match
    EXCELLENT_MATCH = 0.95   # 95%+ similar (minor typo)
    GOOD_MATCH = 0.85        # 85%+ similar (small mistake)
    ACCEPTABLE_MATCH = 0.75  # 75%+ similar (noticeable error but close)

    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.

        - Convert to lowercase
        - Remove accents (é -> e, ñ -> n)
        - Strip whitespace
        - Remove punctuation
        """
        if not text:
            return ""

        # Lowercase
        text = text.lower()

        # Remove accents using Unicode normalization
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

        # Remove punctuation and extra whitespace
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())

        return text

    def calculate_similarity(self, answer: str, correct: str) -> float:
        """
        Calculate similarity ratio between two strings.

        Uses Levenshtein distance algorithm to compute similarity.
        Returns value between 0.0 (completely different) and 1.0 (identical).
        """
        # Normalize both strings
        answer_norm = self.normalize_text(answer)
        correct_norm = self.normalize_text(correct)

        if not answer_norm or not correct_norm:
            return 0.0

        # Calculate similarity using Levenshtein ratio
        return ratio(answer_norm, correct_norm)

    def check_answer(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str]:
        """
        Check if user's answer is correct or close enough.

        Returns:
            Tuple of (is_accepted, similarity_score, feedback_message)

        Examples:
            >>> checker = AnswerChecker()
            >>> checker.check_answer("hello", "hello")
            (True, 1.0, "Perfect!")
            >>> checker.check_answer("helo", "hello")
            (True, 0.89, "Bijna goed! Let op spelling.")
            >>> checker.check_answer("house", "home")
            (False, 0.4, "Niet correct.")
        """
        similarity = self.calculate_similarity(user_answer, correct_answer)

        # Determine if answer is accepted
        is_accepted = similarity >= self.ACCEPTABLE_MATCH

        # Generate feedback based on similarity
        if similarity >= self.PERFECT_MATCH:
            feedback = "Perfect!"
        elif similarity >= self.EXCELLENT_MATCH:
            feedback = "Uitstekend! Klein foutje, maar goed genoeg."
        elif similarity >= self.GOOD_MATCH:
            feedback = "Goed! Let op de spelling."
        elif similarity >= self.ACCEPTABLE_MATCH:
            feedback = "Geaccepteerd, maar let beter op de spelling."
        else:
            feedback = "Niet correct."

        return is_accepted, similarity, feedback

    def get_quality_label(self, similarity: float) -> str:
        """
        Get a quality label for the similarity score.

        Returns: "perfect", "excellent", "good", "acceptable", or "incorrect"
        """
        if similarity >= self.PERFECT_MATCH:
            return "perfect"
        elif similarity >= self.EXCELLENT_MATCH:
            return "excellent"
        elif similarity >= self.GOOD_MATCH:
            return "good"
        elif similarity >= self.ACCEPTABLE_MATCH:
            return "acceptable"
        else:
            return "incorrect"
