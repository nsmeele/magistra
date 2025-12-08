from typing import List as ListType
from typing import Optional

from app import db
from app.models import Category, Entry, Language, List


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


class LanguageRepository(BaseRepository):
    """Repository for Language operations"""

    def __init__(self):
        super().__init__(Language)

    def get_all_ordered(self) -> ListType[Language]:
        """Get all languages ordered by name"""
        return self.model.query.order_by(self.model.name).all()

    def get_by_code(self, code: str) -> Optional[Language]:
        """Get a language by its code"""
        return self.model.query.filter_by(code=code).first()


class CategoryRepository(BaseRepository):
    """Repository for Category operations"""

    def __init__(self):
        super().__init__(Category)

    def get_all_ordered(self) -> ListType[Category]:
        """Get all categories ordered by name"""
        return self.model.query.order_by(self.model.name).all()


class ListRepository(BaseRepository):
    """Repository for List operations"""

    def __init__(self):
        super().__init__(List)

    def get_all_ordered(
        self,
        language: Optional[Language] = None,
        category_id: Optional[int] = None,
    ) -> ListType["List"]:
        """Get all lists ordered by creation date (newest first), optionally filtered"""
        query = self.model.query
        if language:
            # Filter op lijsten waar de taal voorkomt in source OF target
            query = query.filter(
                db.or_(
                    self.model.source_language_id == language.id,
                    self.model.target_language_id == language.id,
                )
            )
        if category_id:
            query = query.filter_by(category_id=category_id)
        return query.order_by(self.model.created_at.desc()).all()

    def get_with_entries(self, list_id: int) -> Optional["List"]:
        """Get a list with all its entries loaded"""
        return self.model.query.filter_by(id=list_id).first()

    def create_list(
        self,
        name: str,
        source_language_id: int,
        target_language_id: int,
        category_id: Optional[int] = None,
    ) -> "List":
        """Create a new list"""
        return self.create(
            name=name,
            source_language_id=source_language_id,
            target_language_id=target_language_id,
            category_id=category_id,
        )


class EntryRepository(BaseRepository):
    """Repository for Entry operations"""

    def __init__(self):
        super().__init__(Entry)

    def get_by_list(self, list_id: int) -> ListType[Entry]:
        """Get all entries for a specific list"""
        return self.model.query.filter_by(list_id=list_id).all()

    def create_entry(
        self, list_id: int, source_word: str, target_word: str, entry_type: str = "word"
    ) -> Entry:
        """Create a new entry"""
        return self.create(
            list_id=list_id,
            source_word=source_word,
            target_word=target_word,
            entry_type=entry_type,
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

    def get_all_with_list(self) -> ListType[Entry]:
        """Get all entries with their list data, ordered by creation date"""
        return (
            self.model.query.join(List)
            .order_by(self.model.created_at.desc())
            .all()
        )
