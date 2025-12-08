import random
from datetime import datetime
from typing import Dict
from typing import List as ListType
from typing import Optional, Tuple

from app import db
from app.models import (
    Category,
    Entry,
    Language,
    List,
    QuizAnswer,
    QuizSession,
    QuizSessionList,
)
from app.repositories import (
    CategoryRepository,
    EntryRepository,
    LanguageRepository,
    ListRepository,
)


class LanguageService:
    """Service for language operations"""

    def __init__(self):
        self.language_repo = LanguageRepository()

    def get_all_languages(self) -> ListType[Language]:
        """Get all languages"""
        return self.language_repo.get_all_ordered()

    def get_language_by_id(self, language_id: int) -> Optional[Language]:
        """Get a specific language"""
        return self.language_repo.get_by_id(language_id)


class CategoryService:
    """Service for category operations"""

    def __init__(self):
        self.category_repo = CategoryRepository()

    def get_all_categories(self) -> ListType[Category]:
        """Get all categories"""
        return self.category_repo.get_all_ordered()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get a specific category"""
        return self.category_repo.get_by_id(category_id)

    def create_category(self, name: str) -> Category:
        """Create a new category"""
        if not name:
            raise ValueError("Category name is required")
        return self.category_repo.create(name=name)


class ListService:
    """Service for list business logic"""

    def __init__(self):
        self.list_repo = ListRepository()
        self.entry_repo = EntryRepository()

    def get_all_lists(
        self,
        language_id: Optional[int] = None,
        language_name: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> ListType[List]:
        """Get all lists ordered by creation date, optionally filtered"""
        return self.list_repo.get_all_ordered(
            language_id=language_id,
            language_name=language_name,
            category_id=category_id,
        )

    def get_list_by_id(self, list_id: int) -> Optional[List]:
        """Get a specific list"""
        return self.list_repo.get_by_id(list_id)

    def get_entry_by_id(self, entry_id: int) -> Optional[Entry]:
        """Get a specific entry"""
        return self.entry_repo.get_by_id(entry_id)

    def create_list(
        self,
        name: str,
        source_language: str,
        target_language: str,
        language_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> List:
        """Create a new list"""
        if not all([name, source_language, target_language]):
            raise ValueError("All fields are required")
        return self.list_repo.create_list(
            name, source_language, target_language, language_id, category_id
        )

    def delete_list(self, list_id: int) -> None:
        """Delete a list"""
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")
        self.list_repo.delete(vocab_list)

    def add_entry_to_list(
        self, list_id: int, source_word: str, target_word: str, entry_type: str = "word"
    ) -> Entry:
        """Add an entry to a list"""
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")

        if not all([source_word, target_word]):
            raise ValueError("Both source and target are required")

        return self.entry_repo.create_entry(
            list_id, source_word, target_word, entry_type
        )

    def update_entry(
        self, entry_id: int, source_word: str, target_word: str, entry_type: str
    ) -> Entry:
        """Update an existing entry"""
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        if not all([source_word, target_word]):
            raise ValueError("Both source and target are required")

        return self.entry_repo.update(
            entry,
            source_word=source_word,
            target_word=target_word,
            entry_type=entry_type,
        )

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

    def initialize_quiz(
        self, list_id: int, direction_preference: str = "random"
    ) -> Dict:
        """Initialize a new quiz session

        Args:
            list_id: The ID of the list to quiz
            direction_preference: 'forward', 'reverse', or 'random'
        """
        vocab_list = self.list_repo.get_by_id(list_id)
        if not vocab_list:
            raise ValueError(f"List with id {list_id} not found")

        if not vocab_list.entries:
            raise ValueError("Cannot start quiz: list has no entries")

        # Create quiz questions with directions based on preference
        # Each question is a dict with entry_id and direction ('forward' or 'reverse')
        quiz_questions = []
        for entry in vocab_list.entries:
            if direction_preference == "random":
                direction = random.choice(["forward", "reverse"])
            else:
                direction = direction_preference
            quiz_questions.append({"entry_id": entry.id, "direction": direction})

        # Shuffle questions for random order
        random.shuffle(quiz_questions)

        return {
            "quiz_questions": quiz_questions,
            "quiz_list_id": list_id,
            "quiz_index": 0,
            "quiz_score": 0,
            "quiz_total": len(quiz_questions),
        }

    def initialize_mixed_quiz(
        self, list_ids: ListType[int], direction_preference: str = "random"
    ) -> Dict:
        """Initialize a quiz session from multiple lists with matching languages

        Args:
            list_ids: List of list IDs to include in the quiz
            direction_preference: 'forward', 'reverse', or 'random'
        """
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
            elif (
                vocab_list.source_language != source_lang
                or vocab_list.target_language != target_lang
            ):
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
            raise ValueError(
                "Kan quiz niet starten: geen items gevonden in geselecteerde lijsten"
            )

        # Create quiz questions with directions based on preference
        quiz_questions = []
        for entry in all_entries:
            if direction_preference == "random":
                direction = random.choice(["forward", "reverse"])
            else:
                direction = direction_preference
            quiz_questions.append({"entry_id": entry.id, "direction": direction})

        # Shuffle questions for random order
        random.shuffle(quiz_questions)

        return {
            "quiz_questions": quiz_questions,
            "quiz_list_ids": list_ids,  # Store multiple list IDs
            "quiz_list_names": list_names,  # Store list names for display
            "quiz_source_language": source_lang,
            "quiz_target_language": target_lang,
            "quiz_index": 0,
            "quiz_score": 0,
            "quiz_total": len(quiz_questions),
        }

    def get_current_question(
        self, quiz_data: Dict
    ) -> Tuple[Optional[Entry], Dict, str, str]:
        """
        Get the current quiz question
        Returns: (entry, updated_quiz_data, progress_string, direction) or (None, quiz_data, '', '') if quiz is complete
        """
        quiz_index = quiz_data.get("quiz_index", 0)
        quiz_questions = quiz_data.get("quiz_questions", [])

        if quiz_index >= len(quiz_questions):
            return None, quiz_data, "", ""

        # Try to find a valid entry, skipping deleted ones
        while quiz_index < len(quiz_questions):
            question = quiz_questions[quiz_index]
            entry_id = question["entry_id"]
            direction = question["direction"]
            entry = self.entry_repo.get_by_id(entry_id)

            if entry:
                # Found a valid entry
                # Update quiz_data with the potentially skipped index
                quiz_data["quiz_index"] = quiz_index
                progress = f"{quiz_index + 1}/{len(quiz_questions)}"
                return entry, quiz_data, progress, direction

            # Entry was deleted, move to next one
            quiz_index += 1

        # All remaining entries were deleted
        return None, quiz_data, "", ""

    def check_answer(
        self, entry_id: int, user_answer: str, direction: str = "forward"
    ) -> Tuple[bool, str]:
        """
        Check if the user's answer is correct
        Returns: (is_correct, correct_answer)
        """
        entry = self.entry_repo.get_by_id(entry_id)
        if not entry:
            raise ValueError(f"Entry with id {entry_id} not found")

        # Determine the correct answer based on direction
        if direction == "forward":
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
        If incorrect, add the question back to the end of the queue
        Returns: updated quiz_data
        """
        quiz_index = quiz_data.get("quiz_index", 0)
        quiz_questions = quiz_data.get("quiz_questions", [])

        if is_correct:
            # Move to next question and increment score
            quiz_data["quiz_score"] = quiz_data.get("quiz_score", 0) + 1
            quiz_data["quiz_index"] = quiz_index + 1
        else:
            # Re-add the current question to the end of the queue
            if quiz_index < len(quiz_questions):
                current_question = quiz_questions[quiz_index]
                quiz_questions.append(current_question)
                quiz_data["quiz_questions"] = quiz_questions
            # Move to next question (the incorrect one is now also at the end)
            quiz_data["quiz_index"] = quiz_index + 1

        return quiz_data

    def is_quiz_complete(self, quiz_data: Dict) -> bool:
        """Check if the quiz is complete"""
        quiz_index = quiz_data.get("quiz_index", 0)
        quiz_questions = quiz_data.get("quiz_questions", [])
        return quiz_index >= len(quiz_questions)

    def get_quiz_results(self, quiz_data: Dict) -> Dict:
        """Get the final quiz results"""
        # Use quiz_total if available (original question count), otherwise fall back to questions length
        total = quiz_data.get("quiz_total", len(quiz_data.get("quiz_questions", [])))
        return {
            "score": quiz_data.get("quiz_score", 0),
            "total": total,
        }

    def create_or_update_session(
        self, quiz_data: Dict, session_id: Optional[int] = None
    ) -> QuizSession:
        """
        Create a new quiz session or update existing one (for resume)

        Args:
            quiz_data: Quiz session data from Flask session
            session_id: Optional existing session ID to update

        Returns:
            QuizSession object
        """
        is_mixed = "quiz_list_ids" in quiz_data
        quiz_type = "mixed" if is_mixed else "single"
        direction = quiz_data.get("direction", "random")

        if session_id:
            # Update existing session
            session = QuizSession.query.get(session_id)
            if session:
                session.current_index = quiz_data.get("quiz_index", 0)
                session.correct_answers = quiz_data.get("quiz_score", 0)
                session.quiz_data = quiz_data
                db.session.commit()
                return session

        # Create new session
        # Use quiz_total if available (original question count), otherwise fall back to questions length
        total = quiz_data.get("quiz_total", len(quiz_data.get("quiz_questions", [])))
        session = QuizSession(
            quiz_type=quiz_type,
            direction=direction,
            total_questions=total,
            correct_answers=quiz_data.get("quiz_score", 0),
            current_index=quiz_data.get("quiz_index", 0),
            status="in_progress",
            quiz_data=quiz_data,
        )
        db.session.add(session)
        db.session.flush()

        # Link lists to session
        if is_mixed:
            list_ids = quiz_data.get("quiz_list_ids", [])
        else:
            list_ids = [quiz_data.get("quiz_list_id")]

        for list_id in list_ids:
            if list_id:
                session_list = QuizSessionList(session_id=session.id, list_id=list_id)
                db.session.add(session_list)

        db.session.commit()
        return session

    def save_quiz_answer(self, session_id: int, answer_data: Dict) -> QuizAnswer:
        """
        Save a single quiz answer to an existing session

        Args:
            session_id: The quiz session ID
            answer_data: Dict with entry_id, user_answer, correct_answer, is_correct, direction

        Returns:
            Created QuizAnswer object
        """
        answer = QuizAnswer(
            session_id=session_id,
            entry_id=answer_data["entry_id"],
            user_answer=answer_data["user_answer"],
            correct_answer=answer_data["correct_answer"],
            is_correct=answer_data["is_correct"],
            question_direction=answer_data["direction"],
        )
        db.session.add(answer)
        db.session.commit()
        return answer

    def complete_quiz_session(self, session_id: int, final_score: int) -> QuizSession:
        """
        Mark a quiz session as completed

        Args:
            session_id: The quiz session ID
            final_score: Final correct answers count

        Returns:
            Updated QuizSession object
        """
        session = QuizSession.query.get(session_id)
        if session:
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.correct_answers = final_score

            # Calculate duration if we have started_at
            if session.started_at:
                duration = datetime.utcnow() - session.started_at
                session.duration_seconds = int(duration.total_seconds())

            db.session.commit()
        return session

    def save_quiz_session(
        self, quiz_data: Dict, all_answers: ListType[Dict]
    ) -> QuizSession:
        """
        Save completed quiz session to database (legacy method for backward compatibility)

        Args:
            quiz_data: Quiz session data from Flask session
            all_answers: List of answer dicts

        Returns:
            Created QuizSession object
        """
        # Determine quiz type
        is_mixed = "quiz_list_ids" in quiz_data
        quiz_type = "mixed" if is_mixed else "single"

        # Get direction from quiz_data
        direction = quiz_data.get("direction", "random")
        if direction == "random":
            directions = set(
                q.get("direction") for q in quiz_data.get("quiz_questions", [])
            )
            if len(directions) == 1:
                direction = directions.pop()

        # Create quiz session as completed
        # Use quiz_total if available (original question count), otherwise fall back to questions length
        total = quiz_data.get("quiz_total", len(quiz_data.get("quiz_questions", [])))
        session = QuizSession(
            quiz_type=quiz_type,
            direction=direction,
            total_questions=total,
            correct_answers=quiz_data.get("quiz_score", 0),
            current_index=total,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            quiz_data=quiz_data,
        )
        db.session.add(session)
        db.session.flush()

        # Create quiz answers
        for answer_data in all_answers:
            answer = QuizAnswer(
                session_id=session.id,
                entry_id=answer_data["entry_id"],
                user_answer=answer_data["user_answer"],
                correct_answer=answer_data["correct_answer"],
                is_correct=answer_data["is_correct"],
                question_direction=answer_data["direction"],
            )
            db.session.add(answer)

        # Link lists to session
        if is_mixed:
            list_ids = quiz_data.get("quiz_list_ids", [])
        else:
            list_ids = [quiz_data.get("quiz_list_id")]

        for list_id in list_ids:
            if list_id:
                session_list = QuizSessionList(session_id=session.id, list_id=list_id)
                db.session.add(session_list)

        db.session.commit()
        return session

    def get_quiz_history(
        self, limit: Optional[int] = None, status: Optional[str] = "completed"
    ) -> ListType[QuizSession]:
        """Get quiz history ordered by completion date (newest first)"""
        query = QuizSession.query
        if status:
            query = query.filter_by(status=status)

        if status == "completed":
            query = query.order_by(QuizSession.completed_at.desc())
        else:
            query = query.order_by(QuizSession.started_at.desc())

        if limit:
            query = query.limit(limit)
        return query.all()

    def get_incomplete_sessions(self) -> ListType[QuizSession]:
        """Get all incomplete quiz sessions"""
        return (
            QuizSession.query.filter_by(status="in_progress")
            .order_by(QuizSession.started_at.desc())
            .all()
        )

    def get_quiz_session_detail(self, session_id: int) -> Optional[QuizSession]:
        """Get detailed quiz session with all answers"""
        return QuizSession.query.filter_by(id=session_id).first()

    def get_difficult_entries(
        self, list_id: Optional[int] = None, min_attempts: int = 2, limit: int = 15
    ) -> ListType[Entry]:
        """
        Get entries with low success rate for smart practice

        Args:
            list_id: Optional filter by specific list
            min_attempts: Minimum attempts needed to be considered
            limit: Maximum number of entries to return

        Returns:
            List of entries ordered by success rate (worst first)
        """
        query = Entry.query.filter(
            (Entry.correct_count + Entry.incorrect_count) >= min_attempts
        )

        if list_id:
            query = query.filter_by(list_id=list_id)

        # Order by success rate (calculated as correct / total)
        # SQLAlchemy expression for success rate
        total_attempts = Entry.correct_count + Entry.incorrect_count
        success_rate = Entry.correct_count * 100.0 / total_attempts

        entries = query.all()

        # Sort in Python since we need the property
        entries_with_rate = [(entry, entry.success_rate or 0) for entry in entries]
        entries_with_rate.sort(key=lambda x: x[1])

        return [entry for entry, _ in entries_with_rate[:limit]]
