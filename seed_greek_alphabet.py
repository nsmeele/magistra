#!/usr/bin/env python3
"""
Seed script for Greek alphabet list with all letters and combination letters
"""

from app import create_app, db
from app.models import Entry, Language, List, QuizSession


def seed_greek_alphabet():
    app = create_app()

    with app.app_context():
        # Get or create Greek language
        greek_language = Language.query.filter_by(code="el").first()
        if not greek_language:
            print("Greek language not found, creating it...")
            greek_language = Language(name="Greek", code="el")
            db.session.add(greek_language)
            db.session.commit()

        # Get or create Latin language
        latin_language = Language.query.filter_by(code="la").first()
        if not latin_language:
            print("Latin language not found, creating it...")
            latin_language = Language(name="Latin", code="la")
            db.session.add(latin_language)
            db.session.commit()

        # Check if old lists exist and delete them (including related quiz sessions)
        old_list_names = ["Grieks Alfabet", "Grieks Alfabet - Letters", "Grieks Alfabet - Combinaties"]
        for list_name in old_list_names:
            existing_list = List.query.filter_by(name=list_name).first()
            if existing_list:
                print(f"List '{list_name}' already exists. Deleting it first...")

                # First, delete any quiz sessions that reference this list
                # We need to delete QuizSessionList entries manually
                db.session.execute(
                    db.text("DELETE FROM quiz_session_lists WHERE list_id = :list_id"),
                    {"list_id": existing_list.id}
                )

                # Now we can safely delete the list
                db.session.delete(existing_list)

        db.session.commit()

        # Greek alphabet letters: Greek letter -> Latin transliteration
        alphabet = [
            ("α", "a"),
            ("β", "b"),
            ("γ", "g"),
            ("δ", "d"),
            ("ε", "e"),
            ("ζ", "z"),
            ("η", "è / ē"),
            ("θ", "th"),
            ("ι", "i"),
            ("κ", "k"),
            ("λ", "l"),
            ("μ", "m"),
            ("ν", "n"),
            ("ξ", "x"),
            ("ο", "o"),
            ("π", "p"),
            ("ρ", "r"),
            ("σ", "s"),
            ("ς", "s"),
            ("τ", "t"),
            ("υ", "u / y"),
            ("φ", "f / ph"),
            ("χ", "ch"),
            ("ψ", "ps"),
            ("ω", "ō / ō"),
        ]

        # Greek combination letters (digraphs): Greek -> Latin transliteration
        combinations = [
            ("αι", "ai"),
            ("ει", "ei"),
            ("οι", "oi"),
            ("υι", "ui"),
            ("αυ", "au"),
            ("ευ", "eu"),
            ("ηυ", "ēu"),
            ("ου", "ou"),
            ("γγ", "ng"),
            ("γκ", "nk"),
            ("γξ", "nx"),
            ("γχ", "nch"),
            ("μπ", "mp"),
            ("ντ", "nt"),
            ("τζ", "tz"),
            ("τσ", "ts"),
        ]

        # Create FIRST list: Alfabetletters
        print("Creating list 'Grieks Alfabet - Letters'...")
        letters_list = List(
            name="Grieks Alfabet - Letters",
            source_language=greek_language,
            target_language=latin_language,
        )
        db.session.add(letters_list)
        db.session.flush()  # Flush to get the ID without committing

        # Add alphabet entries to first list
        for greek_letter, transliteration in alphabet:
            entry = Entry(
                list_id=letters_list.id,
                source_word=greek_letter,
                target_word=transliteration,
                entry_type="letter",
            )
            db.session.add(entry)

        # Create SECOND list: Combinatieletters
        print("Creating list 'Grieks Alfabet - Combinaties'...")
        combinations_list = List(
            name="Grieks Alfabet - Combinaties",
            source_language=greek_language,
            target_language=latin_language,
        )
        db.session.add(combinations_list)
        db.session.flush()  # Flush to get the ID without committing

        # Add combination entries to second list
        for greek_combo, transliteration in combinations:
            entry = Entry(
                list_id=combinations_list.id,
                source_word=greek_combo,
                target_word=transliteration,
                entry_type="letter",
            )
            db.session.add(entry)

        # Commit everything at once
        db.session.commit()

        print(f"\nSuccessfully seeded Greek alphabet lists:")
        print(f"  - Grieks Alfabet - Letters: {len(alphabet)} entries")
        print(f"  - Grieks Alfabet - Combinaties: {len(combinations)} entries")


if __name__ == "__main__":
    seed_greek_alphabet()