#!/usr/bin/env python3
"""
Seed script for Latin verbs with multiple tenses (Praesens, Imperfectum, Perfectum, Futurum):
habere (to have), esse (to be), velle (to want),
scandere (to climb), natare (to swim), ire (to go), currere (to run),
canere (to sing), saltare (to dance), posse (to be able to/can),
lavare (to wash), rogare (to ask), amare (to love), videre (to see),
audire (to hear), dicere (to say), facere (to do/make), venire (to come),
scribere (to write), legere (to read), dare (to give), capere (to take),
ambulare (to walk)
"""

from app import create_app, db
from app.constants import EntryType
from app.models import Entry, Language, List
from app.seed_data import LATIN_VERBS, OLD_LATIN_LIST_NAMES


def seed_extended_latin_verbs():
    app = create_app()

    with app.app_context():
        verbs_data = LATIN_VERBS
        old_list_names = OLD_LATIN_LIST_NAMES

        # Get or create Latijn language
        latin_language = Language.query.filter_by(code="la").first()
        if not latin_language:
            print("Latijn language not found, creating it...")
            latin_language = Language(name="Latijn", code="la")
            db.session.add(latin_language)
            db.session.commit()

        # Get or create Engels language
        english_language = Language.query.filter_by(code="en").first()
        if not english_language:
            print("Engels language not found, creating it...")
            english_language = Language(name="Engels", code="en")
            db.session.add(english_language)
            db.session.commit()

        # Check if lists already exist (both new and old names)
        list_names = [verb["name"] for verb in verbs_data]
        all_names_to_check = list_names + old_list_names
        existing_lists = List.query.filter(List.name.in_(all_names_to_check)).all()

        if existing_lists:
            print(
                f"Found {len(existing_lists)} existing list(s). Deleting them first..."
            )
            for lst in existing_lists:
                db.session.delete(lst)
            db.session.commit()

        total_conjugations = 0

        # Create lists and entries for each verb
        for verb_data in verbs_data:
            print(f"Creating list for '{verb_data['name']}'...")

            verb_list = List(
                name=verb_data["name"],
                source_language=latin_language,
                target_language=english_language,
            )
            db.session.add(verb_list)
            db.session.flush()

            for latin, english in verb_data["conjugations"]:
                entry = Entry(
                    list_id=verb_list.id,
                    source_word=latin,
                    target_word=english,
                    entry_type=EntryType.VERB.value,
                )
                db.session.add(entry)
                total_conjugations += 1

        # Commit all changes
        db.session.commit()

        print(f"\nSuccessfully seeded {len(verbs_data)} Latin verb lists:")
        for verb_data in verbs_data:
            print(
                f"  - {verb_data['name']}: {len(verb_data['conjugations'])} conjugations"
            )
        print(
            f"\nTotal: {len(verbs_data)} lists with {total_conjugations} verb conjugations"
        )


if __name__ == "__main__":
    seed_extended_latin_verbs()
