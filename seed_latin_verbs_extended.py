#!/usr/bin/env python3
"""
Seed script for Latin verbs:
habere (to have), esse (to be), velle (to want),
scandere (to climb), natare (to swim), ire (to go), currere (to run),
canere (to sing), saltare (to dance), posse (to be able to/can),
lavare (to wash), rogare (to ask)
"""

from app import create_app, db
from app.models import List, Entry

def seed_extended_latin_verbs():
    app = create_app()

    with app.app_context():
        verbs_data = [
            {
                'name': 'habere - to have',
                'conjugations': [
                    ('habeo', 'I have'),
                    ('habes', 'you have'),
                    ('habet', 'he/she/it has'),
                    ('habemus', 'we have'),
                    ('habetis', 'you (plural) have'),
                    ('habent', 'they have'),
                ]
            },
            {
                'name': 'esse - to be',
                'conjugations': [
                    ('sum', 'I am'),
                    ('es', 'you are'),
                    ('est', 'he/she/it is'),
                    ('sumus', 'we are'),
                    ('estis', 'you (plural) are'),
                    ('sunt', 'they are'),
                ]
            },
            {
                'name': 'velle - to want',
                'conjugations': [
                    ('volo', 'I want'),
                    ('vis', 'you want'),
                    ('vult', 'he/she/it wants'),
                    ('volumus', 'we want'),
                    ('vultis', 'you (plural) want'),
                    ('volunt', 'they want'),
                ]
            },
            {
                'name': 'scandere - to climb',
                'conjugations': [
                    ('scando', 'I climb'),
                    ('scandis', 'you climb'),
                    ('scandit', 'he/she/it climbs'),
                    ('scandimus', 'we climb'),
                    ('scanditis', 'you (plural) climb'),
                    ('scandunt', 'they climb'),
                ]
            },
            {
                'name': 'natare - to swim',
                'conjugations': [
                    ('nato', 'I swim'),
                    ('natas', 'you swim'),
                    ('natat', 'he/she/it swims'),
                    ('natamus', 'we swim'),
                    ('natatis', 'you (plural) swim'),
                    ('natant', 'they swim'),
                ]
            },
            {
                'name': 'ire - to go',
                'conjugations': [
                    ('eo', 'I go'),
                    ('is', 'you go'),
                    ('it', 'he/she/it goes'),
                    ('imus', 'we go'),
                    ('itis', 'you (plural) go'),
                    ('eunt', 'they go'),
                ]
            },
            {
                'name': 'currere - to run',
                'conjugations': [
                    ('curro', 'I run'),
                    ('curris', 'you run'),
                    ('currit', 'he/she/it runs'),
                    ('currimus', 'we run'),
                    ('curritis', 'you (plural) run'),
                    ('currunt', 'they run'),
                ]
            },
            {
                'name': 'canere - to sing',
                'conjugations': [
                    ('cano', 'I sing'),
                    ('canis', 'you sing'),
                    ('canit', 'he/she/it sings'),
                    ('canimus', 'we sing'),
                    ('canitis', 'you (plural) sing'),
                    ('canunt', 'they sing'),
                ]
            },
            {
                'name': 'saltare - to dance',
                'conjugations': [
                    ('salto', 'I dance'),
                    ('saltas', 'you dance'),
                    ('saltat', 'he/she/it dances'),
                    ('saltamus', 'we dance'),
                    ('saltatis', 'you (plural) dance'),
                    ('saltant', 'they dance'),
                ]
            },
            {
                'name': 'posse - to be able to/can',
                'conjugations': [
                    ('possum', 'I can/am able'),
                    ('potes', 'you can/are able'),
                    ('potest', 'he/she/it can/is able'),
                    ('possumus', 'we can/are able'),
                    ('potestis', 'you (plural) can/are able'),
                    ('possunt', 'they can/are able'),
                ]
            },
            {
                'name': 'lavare - to wash',
                'conjugations': [
                    ('lavo', 'I wash'),
                    ('lavas', 'you wash'),
                    ('lavat', 'he/she/it washes'),
                    ('lavamus', 'we wash'),
                    ('lavatis', 'you (plural) wash'),
                    ('lavant', 'they wash'),
                ]
            },
            {
                'name': 'rogare - to ask',
                'conjugations': [
                    ('rogo', 'I ask'),
                    ('rogas', 'you ask'),
                    ('rogat', 'he/she/it asks'),
                    ('rogamus', 'we ask'),
                    ('rogatis', 'you (plural) ask'),
                    ('rogant', 'they ask'),
                ]
            },
        ]

        # Check if lists already exist
        list_names = [verb['name'] for verb in verbs_data]
        existing_lists = List.query.filter(List.name.in_(list_names)).all()

        if existing_lists:
            print(f"Found {len(existing_lists)} existing list(s). Deleting them first...")
            for lst in existing_lists:
                db.session.delete(lst)
            db.session.commit()

        total_conjugations = 0

        # Create lists and entries for each verb
        for verb_data in verbs_data:
            print(f"Creating list for '{verb_data['name']}'...")

            verb_list = List(
                name=verb_data['name'],
                source_language='Latin',
                target_language='English'
            )
            db.session.add(verb_list)
            db.session.flush()

            for latin, english in verb_data['conjugations']:
                entry = Entry(
                    list_id=verb_list.id,
                    source_word=latin,
                    target_word=english,
                    entry_type='verb'
                )
                db.session.add(entry)
                total_conjugations += 1

        # Commit all changes
        db.session.commit()

        print(f"\nSuccessfully seeded {len(verbs_data)} Latin verb lists:")
        for verb_data in verbs_data:
            print(f"  - {verb_data['name']}: {len(verb_data['conjugations'])} conjugations")
        print(f"\nTotal: {len(verbs_data)} lists with {total_conjugations} verb conjugations")

if __name__ == '__main__':
    seed_extended_latin_verbs()