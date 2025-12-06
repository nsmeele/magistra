from typing import List, Optional, Dict, Tuple
import random
from app.repositories import WordListRepository, WordRepository
from app.models import WordList, Word


class WordListService:
    """Service for word list business logic"""

    def __init__(self):
        self.list_repo = WordListRepository()
        self.word_repo = WordRepository()

    def get_all_lists(self) -> List[WordList]:
        """Get all word lists ordered by creation date"""
        return self.list_repo.get_all_ordered()

    def get_list_by_id(self, list_id: int) -> Optional[WordList]:
        """Get a specific word list"""
        return self.list_repo.get_by_id(list_id)

    def create_list(self, name: str, source_language: str, target_language: str) -> WordList:
        """Create a new word list"""
        if not all([name, source_language, target_language]):
            raise ValueError("All fields are required")
        return self.list_repo.create_list(name, source_language, target_language)

    def delete_list(self, list_id: int) -> None:
        """Delete a word list"""
        word_list = self.list_repo.get_by_id(list_id)
        if not word_list:
            raise ValueError(f"Word list with id {list_id} not found")
        self.list_repo.delete(word_list)

    def add_word_to_list(self, list_id: int, source_word: str, target_word: str) -> Word:
        """Add a word to a list"""
        word_list = self.list_repo.get_by_id(list_id)
        if not word_list:
            raise ValueError(f"Word list with id {list_id} not found")

        if not all([source_word, target_word]):
            raise ValueError("Both words are required")

        return self.word_repo.create_word(list_id, source_word, target_word)

    def delete_word(self, word_id: int) -> int:
        """Delete a word and return its list_id"""
        word = self.word_repo.get_by_id(word_id)
        if not word:
            raise ValueError(f"Word with id {word_id} not found")

        list_id = word.list_id
        self.word_repo.delete(word)
        return list_id


class QuizService:
    """Service for quiz functionality"""

    def __init__(self):
        self.list_repo = WordListRepository()
        self.word_repo = WordRepository()

    def initialize_quiz(self, list_id: int) -> Dict:
        """Initialize a new quiz session"""
        word_list = self.list_repo.get_by_id(list_id)
        if not word_list:
            raise ValueError(f"Word list with id {list_id} not found")

        if not word_list.words:
            raise ValueError("Cannot start quiz: list has no words")

        # Shuffle word IDs for random order
        word_ids = [w.id for w in word_list.words]
        random.shuffle(word_ids)

        return {
            'quiz_words': word_ids,
            'quiz_list_id': list_id,
            'quiz_index': 0,
            'quiz_score': 0
        }

    def get_current_question(self, quiz_data: Dict) -> Tuple[Optional[Word], str]:
        """
        Get the current quiz question
        Returns: (word, progress_string) or (None, '') if quiz is complete
        """
        quiz_index = quiz_data.get('quiz_index', 0)
        quiz_words = quiz_data.get('quiz_words', [])

        if quiz_index >= len(quiz_words):
            return None, ''

        word_id = quiz_words[quiz_index]
        word = self.word_repo.get_by_id(word_id)
        progress = f"{quiz_index + 1}/{len(quiz_words)}"

        return word, progress

    def check_answer(self, word_id: int, user_answer: str) -> Tuple[bool, str]:
        """
        Check if the user's answer is correct
        Returns: (is_correct, correct_answer)
        """
        word = self.word_repo.get_by_id(word_id)
        if not word:
            raise ValueError(f"Word with id {word_id} not found")

        correct_answer = word.target_word.strip().lower()
        user_answer_clean = user_answer.strip().lower()
        is_correct = user_answer_clean == correct_answer

        # Update word score
        self.word_repo.update_score(word, is_correct)

        return is_correct, word.target_word

    def advance_quiz(self, quiz_data: Dict, is_correct: bool) -> Dict:
        """
        Advance to the next question
        Returns: updated quiz_data
        """
        quiz_data['quiz_index'] = quiz_data.get('quiz_index', 0) + 1
        if is_correct:
            quiz_data['quiz_score'] = quiz_data.get('quiz_score', 0) + 1
        return quiz_data

    def is_quiz_complete(self, quiz_data: Dict) -> bool:
        """Check if the quiz is complete"""
        quiz_index = quiz_data.get('quiz_index', 0)
        quiz_words = quiz_data.get('quiz_words', [])
        return quiz_index >= len(quiz_words)

    def get_quiz_results(self, quiz_data: Dict) -> Dict:
        """Get the final quiz results"""
        return {
            'score': quiz_data.get('quiz_score', 0),
            'total': len(quiz_data.get('quiz_words', []))
        }
