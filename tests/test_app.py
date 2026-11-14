def test_app_exists(app):
    """Test that the app exists."""
    assert app is not None


def test_app_is_testing(app):
    """Test that the app is in testing mode."""
    assert app.config["TESTING"]


def test_home_page(client):
    """Test that the home page loads."""
    response = client.get("/")
    assert response.status_code == 200


def test_import_samples_creates_lists_once(client):
    """Importing the sample lists twice must not create duplicates."""
    from app.models import Entry, Language, List
    from app.seed_data import LATIN_VERBS

    expected_lists = len(LATIN_VERBS) + 2  # plus two Greek alphabet lists

    response = client.post("/import-samples", follow_redirects=True)
    assert response.status_code == 200
    assert List.query.count() == expected_lists
    assert Language.query.count() == 4
    entries_after_first = Entry.query.count()
    assert entries_after_first > 0

    client.post("/import-samples", follow_redirects=True)
    assert List.query.count() == expected_lists
    assert Entry.query.count() == entries_after_first
