from typing import List, Optional
from app import db
from app.models import WordList, Word


class BaseRepository:
    """Base repository class with common CRUD operations"""

    def __init__(self, model):
        self.model = model

    def get_by_id(self, id: int) -> Optional[object]:
        """Get a single record by ID"""
        return self.model.query.get(id)

    def get_all(self) -> List[object]:
        """Get all records"""
        return self.model.query.all()

    def create(self, **kwargs) -> object:
        """Create a new record"""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, instance: object, **kwargs) -> object:
        """Update an existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, instance: object) -> None:
        """Delete a record"""
        db.session.delete(instance)
        db.session.commit()


class WordListRepository(BaseRepository):
    """Repository for WordList operations"""

    def __init__(self):
        super().__init__(WordList)

    def get_all_ordered(self) -> List[WordList]:
        """Get all word lists ordered by creation date (newest first)"""
        return self.model.query.order_by(self.model.created_at.desc()).all()

    def get_with_words(self, list_id: int) -> Optional[WordList]:
        """Get a word list with all its words loaded"""
        return self.model.query.filter_by(id=list_id).first()

    def create_list(self, name: str, source_language: str, target_language: str) -> WordList:
        """Create a new word list"""
        return self.create(
            name=name,
            source_language=source_language,
            target_language=target_language
        )


class WordRepository(BaseRepository):
    """Repository for Word operations"""

    def __init__(self):
        super().__init__(Word)

    def get_by_list(self, list_id: int) -> List[Word]:
        """Get all words for a specific list"""
        return self.model.query.filter_by(list_id=list_id).all()

    def create_word(self, list_id: int, source_word: str, target_word: str) -> Word:
        """Create a new word"""
        return self.create(
            list_id=list_id,
            source_word=source_word,
            target_word=target_word
        )

    def update_score(self, word: Word, is_correct: bool) -> Word:
        """Update word score based on quiz answer"""
        if is_correct:
            word.correct_count += 1
        else:
            word.incorrect_count += 1
        db.session.commit()
        return word

    def get_words_by_ids(self, word_ids: List[int]) -> List[Word]:
        """Get multiple words by their IDs"""
        return self.model.query.filter(self.model.id.in_(word_ids)).all()
