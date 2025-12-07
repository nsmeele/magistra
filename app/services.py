from typing import List as ListType, Optional, Dict, Tuple
import random
from app.repositories import ListRepository, EntryRepository
from app.models import List, Entry


class ListService:
    """Service for list business logic"""

    def __init__(self):
        self.list_repo = ListRepository()
        self.entry_repo = EntryRepository()

    def get_all_lists(self) -> ListType[List]:
        """Get all lists ordered by creation date"""
        return self.list_repo.get_all_ordered()

    def get_list_by_id(self, list_id: int) -> Optional[List]:
        """Get a specific list"""
        return self.list_repo.get_by_id(list_id)

    def get_entry_by_id(self, entry_id: int) -> Optional[Entry]:
        """Get a specific entry"""
        return self.entry_repo.get_by_id(entry_id)

    def create_list(self, name: str, source_language: str, target_language: str) -> List:
        """Create a new list"""
        if not all([name, source_language, target_language]):
            raise ValueError("All fields are required")
        return self.list_repo.create_list(name, source_language, target_language)

    def delete_list(self, list_id: int) -> None:
        """Delete a list"""
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")
        self.list_repo.delete(vocab_list)

    def add_entry_to_list(self, list_id: int, source_word: str, target_word: str, entry_type: str = 'word') -> Entry:
        """Add an entry to a list"""
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")

        if not all([source_word, target_word]):
            raise ValueError("Both source and target are required")

        return self.entry_repo.create_entry(list_id, source_word, target_word, entry_type)

    def update_entry(self, entry_id: int, source_word: str, target_word: str, entry_type: str) -> Entry:
        """Update an existing entry"""
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        if not all([source_word, target_word]):
            raise ValueError("Both source and target are required")

        return self.entry_repo.update(entry,
                                      source_word=source_word,
                                      target_word=target_word,
                                      entry_type=entry_type)

    def delete_entry(self, entry_id: int) -> int:
        """Delete an entry and return its list_id"""
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        list_id = entry.list_id
        self.entry_repo.delete(entry)
        return list_id


class QuizService:
    """Service for quiz functionality"""

    def __init__(self):
        self.list_repo = ListRepository()
        self.entry_repo = EntryRepository()

    def initialize_quiz(self, list_id: int) -> Dict:
        """Initialize a new quiz session"""
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")

        if not vocab_list.entries:
            raise ValueError("Cannot start quiz: list has no entries")

        # Shuffle entry IDs for random order
        entry_ids = [e.id for e in vocab_list.entries]
        random.shuffle(entry_ids)

        return {
            'quiz_entries': entry_ids,
            'quiz_list_id': list_id,
            'quiz_index': 0,
            'quiz_score': 0
        }

    def get_current_question(self, quiz_data: Dict) -> Tuple[Optional[Entry], str]:
        """
        Get the current quiz question
        Returns: (entry, progress_string) or (None, '') if quiz is complete
        """
        quiz_index = quiz_data.get('quiz_index', 0)
        quiz_entries = quiz_data.get('quiz_entries', [])

        if quiz_index >= len(quiz_entries):
            return None, ''

        entry_id = quiz_entries[quiz_index]
        entry = self.entry_repo.get_by_id(entry_id)
        progress = f"{quiz_index + 1}/{len(quiz_entries)}"

        return entry, progress

    def check_answer(self, entry_id: int, user_answer: str) -> Tuple[bool, str]:
        """
        Check if the user's answer is correct
        Returns: (is_correct, correct_answer)
        """
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        correct_answer = entry.target_word.strip().lower()
        user_answer_clean = user_answer.strip().lower()
        is_correct = user_answer_clean == correct_answer

        # Update entry score
        self.entry_repo.update_score(entry, is_correct)

        return is_correct, entry.target_word

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
        quiz_entries = quiz_data.get('quiz_entries', [])
        return quiz_index >= len(quiz_entries)

    def get_quiz_results(self, quiz_data: Dict) -> Dict:
        """Get the final quiz results"""
        return {
            'score': quiz_data.get('quiz_score', 0),
            'total': len(quiz_data.get('quiz_entries', []))
        }
