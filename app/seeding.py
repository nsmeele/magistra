"""Create the sample languages and lists from app.seed_data.

Used by the "Voorbeeldlijsten importeren" button and by the seed scripts.
Must run inside an application context.
"""

from dataclasses import dataclass

from app import db
from app.constants import EntryType
from app.models import Entry, Language, List
from app.seed_data import (
    GREEK_ALPHABET,
    GREEK_COMBINATIONS,
    GREEK_COMBINATIONS_LIST_NAME,
    GREEK_LETTERS_LIST_NAME,
    LANGUAGES,
    LATIN_VERBS,
)


@dataclass
class SeedResult:
    lists_created: int = 0
    lists_skipped: int = 0
    entries_created: int = 0


def ensure_languages() -> dict:
    """Get or create the sample languages. Returns {code: Language}."""
    by_code = {}
    for data in LANGUAGES:
        language = Language.query.filter_by(code=data["code"]).first()
        if not language:
            language = Language(name=data["name"], code=data["code"])
            db.session.add(language)
        by_code[data["code"]] = language
    db.session.flush()
    return by_code


def _sample_lists(languages: dict):
    """Yield (name, source, target, entry_type, [(source, target, note)])."""
    yield (
        GREEK_LETTERS_LIST_NAME,
        languages["el"],
        languages["la"],
        EntryType.LETTER.value,
        GREEK_ALPHABET,
    )
    yield (
        GREEK_COMBINATIONS_LIST_NAME,
        languages["el"],
        languages["la"],
        EntryType.LETTER.value,
        GREEK_COMBINATIONS,
    )
    for verb in LATIN_VERBS:
        yield (
            verb["name"],
            languages["la"],
            languages["en"],
            EntryType.VERB.value,
            [(latin, english, None) for latin, english in verb["conjugations"]],
        )


def import_sample_lists() -> SeedResult:
    """Add every sample list that doesn't exist yet. Existing lists are left alone."""
    result = SeedResult()
    languages = ensure_languages()
    existing = {name for (name,) in db.session.query(List.name).all()}

    for name, source, target, entry_type, items in _sample_lists(languages):
        if name in existing:
            result.lists_skipped += 1
            continue
        word_list = List(name=name, source_language=source, target_language=target)
        db.session.add(word_list)
        for source_word, target_word, note in items:
            word_list.entries.append(
                Entry(
                    source_word=source_word,
                    target_word=target_word,
                    pronunciation_note=note,
                    entry_type=entry_type,
                )
            )
            result.entries_created += 1
        result.lists_created += 1

    db.session.commit()
    return result
