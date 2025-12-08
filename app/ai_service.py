import json
from abc import ABC, abstractmethod
from typing import List, Optional

from flask import current_app


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def generate_list(
        self,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int = 10,
    ) -> List[dict]:
        """Generate a list of word/sentence pairs"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available"""
        pass

    def _build_prompt(
        self,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int,
    ) -> str:
        """Build the prompt for list generation"""
        if entry_type == "word":
            item_type = "woorden"
            example = '"source": "huis", "target": "house"'
        else:
            item_type = "zinnen"
            example = '"source": "Ik ga naar huis.", "target": "I am going home."'

        return f"""Genereer een lijst van {count} {item_type} over het onderwerp "{topic}".
De brontaal is {source_language} en de doeltaal is {target_language}.

Geef het resultaat ALLEEN als een JSON array met objecten die "source" en "target" bevatten.
Geen andere tekst of uitleg, alleen de JSON array.

Voorbeeld formaat:
[
  {{{example}}},
  ...
]

Zorg ervoor dat:
- Elk item relevant is voor het onderwerp "{topic}"
- De vertalingen correct zijn
- Je exact {count} items genereert
"""

    def _parse_response(self, response_text: str) -> List[dict]:
        """Parse the AI response to extract the list items"""
        # Try to find JSON array in the response
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Find the JSON array
        start_idx = text.find("[")
        end_idx = text.rfind("]") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("Geen geldige JSON array gevonden in het antwoord")

        json_str = text[start_idx:end_idx]
        items = json.loads(json_str)

        # Validate structure
        validated_items = []
        for item in items:
            if isinstance(item, dict) and "source" in item and "target" in item:
                validated_items.append(
                    {"source": str(item["source"]), "target": str(item["target"])}
                )

        if not validated_items:
            raise ValueError("Geen geldige items gevonden in het antwoord")

        return validated_items


class OpenAIProvider(AIProvider):
    """OpenAI (GPT) provider"""

    def is_available(self) -> bool:
        api_key = current_app.config.get("OPENAI_API_KEY")
        return bool(api_key)

    def generate_list(
        self,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int = 10,
    ) -> List[dict]:
        from openai import OpenAI

        api_key = current_app.config.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key niet geconfigureerd")

        client = OpenAI(api_key=api_key)
        prompt = self._build_prompt(
            topic, source_language, target_language, entry_type, count
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Je bent een hulpvaardige assistent die woordenlijsten genereert. Je antwoordt alleen met JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        response_text = response.choices[0].message.content
        return self._parse_response(response_text)


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider"""

    def is_available(self) -> bool:
        api_key = current_app.config.get("ANTHROPIC_API_KEY")
        return bool(api_key)

    def generate_list(
        self,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int = 10,
    ) -> List[dict]:
        import anthropic

        api_key = current_app.config.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key niet geconfigureerd")

        client = anthropic.Anthropic(api_key=api_key)
        prompt = self._build_prompt(
            topic, source_language, target_language, entry_type, count
        )

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text
        return self._parse_response(response_text)


class OllamaProvider(AIProvider):
    """Ollama (local) provider"""

    def is_available(self) -> bool:
        try:
            import ollama

            host = current_app.config.get("OLLAMA_HOST", "http://localhost:11434")
            client = ollama.Client(host=host)
            # Try to list models to check if Ollama is running
            client.list()
            return True
        except Exception:
            return False

    def generate_list(
        self,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int = 10,
    ) -> List[dict]:
        import ollama

        host = current_app.config.get("OLLAMA_HOST", "http://localhost:11434")
        client = ollama.Client(host=host)

        prompt = self._build_prompt(
            topic, source_language, target_language, entry_type, count
        )

        # Try common models
        models_to_try = ["llama3.2", "llama3", "mistral", "gemma2"]
        available_models = [m["name"] for m in client.list().get("models", [])]

        model = None
        for m in models_to_try:
            for available in available_models:
                if m in available:
                    model = available
                    break
            if model:
                break

        if not model and available_models:
            model = available_models[0]

        if not model:
            raise ValueError(
                "Geen Ollama model beschikbaar. Installeer een model met: ollama pull llama3.2"
            )

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

        response_text = response["message"]["content"]
        return self._parse_response(response_text)


class AIService:
    """Service for AI-powered list generation"""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    PROVIDER_NAMES = {
        "openai": "OpenAI (GPT)",
        "anthropic": "Anthropic (Claude)",
        "ollama": "Ollama (Lokaal)",
    }

    def get_available_providers(self) -> List[dict]:
        """Get list of available providers with their status"""
        providers = []
        for key, provider_class in self.PROVIDERS.items():
            provider = provider_class()
            providers.append(
                {
                    "key": key,
                    "name": self.PROVIDER_NAMES[key],
                    "available": provider.is_available(),
                }
            )
        return providers

    def generate_list(
        self,
        provider_key: str,
        topic: str,
        source_language: str,
        target_language: str,
        entry_type: str,
        count: int = 10,
    ) -> List[dict]:
        """Generate a list using the specified provider"""
        if provider_key not in self.PROVIDERS:
            raise ValueError(f"Onbekende AI provider: {provider_key}")

        provider = self.PROVIDERS[provider_key]()

        if not provider.is_available():
            raise ValueError(
                f"Provider {self.PROVIDER_NAMES[provider_key]} is niet beschikbaar"
            )

        return provider.generate_list(
            topic, source_language, target_language, entry_type, count
        )
