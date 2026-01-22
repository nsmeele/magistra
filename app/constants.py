from enum import Enum


class EntryType(str, Enum):
    """Entry type constants met Nederlandse labels"""

    WORD = "word"
    SENTENCE = "sentence"
    LETTER = "letter"
    VERB = "verb"

    @property
    def label(self) -> str:
        """Nederlandse weergave labels"""
        labels = {
            "word": "Woord",
            "sentence": "Zin",
            "letter": "Letter",
            "verb": "Werkwoord",
        }
        return labels.get(self.value, self.value.capitalize())

    @classmethod
    def choices(cls):
        """Returns (value, label) tuples voor WTForms"""
        return [(member.value, member.label) for member in cls]

    @classmethod
    def get_label(cls, value: str) -> str:
        """Safe label lookup met fallback"""
        try:
            return cls(value).label
        except ValueError:
            return value.capitalize()
