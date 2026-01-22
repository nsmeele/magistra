#!/usr/bin/env python3
"""
Seed script for languages (Dutch, English, Latin, Greek)
"""

from app import create_app, db
from app.models import Language


def seed_languages():
    app = create_app()

    with app.app_context():
        languages_data = [
            {"name": "Dutch", "code": "nl"},
            {"name": "English", "code": "en"},
            {"name": "Latin", "code": "la"},
            {"name": "Greek", "code": "el"},
        ]

        for lang_data in languages_data:
            existing = Language.query.filter_by(code=lang_data["code"]).first()
            if existing:
                print(f"Language '{lang_data['name']}' already exists, skipping...")
                continue

            language = Language(name=lang_data["name"], code=lang_data["code"])
            db.session.add(language)
            print(f"Added language: {lang_data['name']} ({lang_data['code']})")

        db.session.commit()
        print("\nLanguages seeded successfully!")

        # Show all languages
        all_languages = Language.query.all()
        print(f"\nTotal languages in database: {len(all_languages)}")
        for lang in all_languages:
            print(f"  - {lang.name} ({lang.code})")


if __name__ == "__main__":
    seed_languages()
