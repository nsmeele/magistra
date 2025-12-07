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

        # Create quiz questions with random directions
        # Each question is a dict with entry_id and direction ('forward' or 'reverse')
        quiz_questions = []
        for entry in vocab_list.entries:
            direction = random.choice(['forward', 'reverse'])
            quiz_questions.append({
                'entry_id': entry.id,
                'direction': direction
            })

        # Shuffle questions for random order
        random.shuffle(quiz_questions)

        return {
            'quiz_questions': quiz_questions,
            'quiz_list_id': list_id,
            'quiz_index': 0,
            'quiz_score': 0
        }

    def initialize_mixed_quiz(self, list_ids: ListType[int]) -> Dict:
        """Initialize a quiz session from multiple lists with matching languages"""
        if not list_ids:
            raise ValueError("Selecteer minimaal één lijst")

        # Fetch all lists and validate languages
        vocab_lists = []
        source_lang = None
        target_lang = None

        for list_id in list_ids:
            vocab_list = self.list_repo.get_by_id(list_id)
            if not vocab_list:
                raise ValueError(f"Lijst met id {list_id} niet gevonden")

            # Check if languages match
            if source_lang is None:
                source_lang = vocab_list.source_language
                target_lang = vocab_list.target_language
            elif vocab_list.source_language != source_lang or vocab_list.target_language != target_lang:
                raise ValueError(
                    f"Alle lijsten moeten dezelfde talen hebben. "
                    f"Verwacht: {source_lang} → {target_lang}, "
                    f"maar '{vocab_list.name}' heeft {vocab_list.source_language} → {vocab_list.target_language}"
                )

            vocab_lists.append(vocab_list)

        # Gather entries from all selected lists
        all_entries = []
        list_names = []

        for vocab_list in vocab_lists:
            if vocab_list.entries:
                all_entries.extend(vocab_list.entries)
                list_names.append(vocab_list.name)

        if not all_entries:
            raise ValueError("Kan quiz niet starten: geen items gevonden in geselecteerde lijsten")

        # Create quiz questions with random directions
        quiz_questions = []
        for entry in all_entries:
            direction = random.choice(['forward', 'reverse'])
            quiz_questions.append({
                'entry_id': entry.id,
                'direction': direction
            })

        # Shuffle questions for random order
        random.shuffle(quiz_questions)

        return {
            'quiz_questions': quiz_questions,
            'quiz_list_ids': list_ids,  # Store multiple list IDs
            'quiz_list_names': list_names,  # Store list names for display
            'quiz_source_language': source_lang,
            'quiz_target_language': target_lang,
            'quiz_index': 0,
            'quiz_score': 0
        }

    def get_current_question(self, quiz_data: Dict) -> Tuple[Optional[Entry], Dict, str, str]:
        """
        Get the current quiz question
        Returns: (entry, updated_quiz_data, progress_string, direction) or (None, quiz_data, '', '') if quiz is complete
        """
        quiz_index = quiz_data.get('quiz_index', 0)
        quiz_questions = quiz_data.get('quiz_questions', [])

        if quiz_index >= len(quiz_questions):
            return None, quiz_data, '', ''

        # Try to find a valid entry, skipping deleted ones
        while quiz_index < len(quiz_questions):
            question = quiz_questions[quiz_index]
            entry_id = question['entry_id']
            direction = question['direction']
            entry = self.entry_repo.get_by_id(entry_id)

            if entry:
                # Found a valid entry
                # Update quiz_data with the potentially skipped index
                quiz_data['quiz_index'] = quiz_index
                progress = f"{quiz_index + 1}/{len(quiz_questions)}"
                return entry, quiz_data, progress, direction

            # Entry was deleted, move to next one
            quiz_index += 1

        # All remaining entries were deleted
        return None, quiz_data, '', ''

    def check_answer(self, entry_id: int, user_answer: str, direction: str = 'forward') -> Tuple[bool, str]:
        """
        Check if the user's answer is correct
        Returns: (is_correct, correct_answer)
        """
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        # Determine the correct answer based on direction
        if direction == 'forward':
            # source -> target (original behavior)
            correct_answer_value = entry.target_word
        else:
            # reverse: target -> source
            correct_answer_value = entry.source_word

        correct_answer = correct_answer_value.strip().lower()
        user_answer_clean = user_answer.strip().lower()
        is_correct = user_answer_clean == correct_answer

        # Update entry score
        self.entry_repo.update_score(entry, is_correct)

        return is_correct, correct_answer_value

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
        quiz_questions = quiz_data.get('quiz_questions', [])
        return quiz_index >= len(quiz_questions)

    def get_quiz_results(self, quiz_data: Dict) -> Dict:
        """Get the final quiz results"""
        return {
            'score': quiz_data.get('quiz_score', 0),
            'total': len(quiz_data.get('quiz_questions', []))
        }
