"""
Test AI generation with Ollama for verb conjugations.
Run manually with: python -m pytest tests/test_ai_ollama.py -v -s
"""

import pytest

from app import create_app


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config["TESTING"] = True
    return app


class TestOllamaVerbConjugation:
    """Test verb conjugation generation with Ollama"""

    def test_latin_verb_ambulare_raw(self, app):
        """Test raw response for Latin verb 'ambulare'"""
        with app.app_context():
            from app.ai_service import OllamaProvider

            provider = OllamaProvider()

            if not provider.is_available():
                pytest.skip("Ollama not available")

            # Get the raw prompt
            prompt = provider._build_prompt(
                topic="werkwoord ambulare",
                source_language="Latin",
                target_language="English",
                entry_type="word",
                count=None,
            )

            print("\n=== PROMPT ===")
            print(prompt)
            print("\n=== END PROMPT ===")

            # Call Ollama directly to see raw response
            import ollama
            from flask import current_app

            host = current_app.config.get("OLLAMA_HOST", "http://localhost:11434")
            client = ollama.Client(host=host)

            # Find model
            available_models = [m.model for m in client.list().models]
            model = available_models[0] if available_models else None

            if not model:
                pytest.skip("No Ollama model available")

            print(f"\n=== Using model: {model} ===")

            response = client.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Je bent een hulpvaardige assistent die woordenlijsten genereert. Je antwoordt alleen met JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            raw_response = response["message"]["content"]
            print("\n=== RAW RESPONSE ===")
            print(raw_response)
            print("\n=== END RAW RESPONSE ===")

            # Try to parse it
            try:
                items = provider._parse_response(raw_response)
                print("\n=== PARSED ITEMS ===")
                for item in items:
                    print(f"  {item['source']} -> {item['target']}")
            except Exception as e:
                print(f"\n=== PARSE ERROR: {e} ===")

    def test_latin_verb_amare_raw(self, app):
        """Test raw response for Latin verb 'amare' (more common)"""
        with app.app_context():
            from app.ai_service import OllamaProvider

            provider = OllamaProvider()

            if not provider.is_available():
                pytest.skip("Ollama not available")

            prompt = provider._build_prompt(
                topic="conjugate amare",
                source_language="Latin",
                target_language="English",
                entry_type="word",
                count=None,
            )

            print("\n=== PROMPT ===")
            print(prompt)

            import ollama
            from flask import current_app

            host = current_app.config.get("OLLAMA_HOST", "http://localhost:11434")
            client = ollama.Client(host=host)
            available_models = [m.model for m in client.list().models]
            model = available_models[0] if available_models else None

            if not model:
                pytest.skip("No Ollama model available")

            response = client.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Latin language expert. You respond only with valid JSON arrays.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            raw_response = response["message"]["content"]
            print("\n=== RAW RESPONSE ===")
            print(raw_response)

            try:
                items = provider._parse_response(raw_response)
                print("\n=== PARSED ITEMS ===")
                for item in items:
                    print(f"  {item['source']} -> {item['target']}")

                # Check for amare forms
                sources = [item["source"].lower() for item in items]
                expected = ["amo", "amas", "amat", "amamus", "amatis", "amant"]
                found = sum(1 for e in expected if any(e in s for s in sources))
                print(f"\nFound {found}/6 expected amare forms")

            except Exception as e:
                print(f"\n=== PARSE ERROR: {e} ===")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
