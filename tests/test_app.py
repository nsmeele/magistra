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
