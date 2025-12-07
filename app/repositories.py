from typing import List as ListType, Optional
from app import db
from app.models import List, Entry


class BaseRepository:
    """Base repository class with common CRUD operations"""

    def __init__(self, model):
        self.model = model

    def get_by_id(self, id: int) -> Optional[object]:
        """Get a single record by ID"""
        return self.model.query.get(id)

    def get_all(self) -> ListType[object]:
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


class ListRepository(BaseRepository):
    """Repository for List operations"""

    def __init__(self):
        super().__init__(List)

    def get_all_ordered(self) -> ListType['List']:
        """Get all lists ordered by creation date (newest first)"""
        return self.model.query.order_by(self.model.created_at.desc()).all()

    def get_with_entries(self, list_id: int) -> Optional['List']:
        """Get a list with all its entries loaded"""
        return self.model.query.filter_by(id=list_id).first()

    def create_list(self, name: str, source_language: str, target_language: str) -> 'List':
        """Create a new list"""
        return self.create(
            name=name,
            source_language=source_language,
            target_language=target_language
        )


class EntryRepository(BaseRepository):
    """Repository for Entry operations"""

    def __init__(self):
        super().__init__(Entry)

    def get_by_list(self, list_id: int) -> ListType[Entry]:
        """Get all entries for a specific list"""
        return self.model.query.filter_by(list_id=list_id).all()

    def create_entry(self, list_id: int, source_word: str, target_word: str, entry_type: str = 'word') -> Entry:
        """Create a new entry"""
        return self.create(
            list_id=list_id,
            source_word=source_word,
            target_word=target_word,
            entry_type=entry_type
        )

    def update_score(self, entry: Entry, is_correct: bool) -> Entry:
        """Update entry score based on quiz answer"""
        if is_correct:
            entry.correct_count += 1
        else:
            entry.incorrect_count += 1
        db.session.commit()
        return entry

    def get_entries_by_ids(self, entry_ids: ListType[int]) -> ListType[Entry]:
        """Get multiple entries by their IDs"""
        return self.model.query.filter(self.model.id.in_(entry_ids)).all()
