from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app.constants import EntryType


class NewListForm(FlaskForm):
    """Form voor het aanmaken van een nieuwe lijst"""

    name = StringField("Naam", validators=[DataRequired(), Length(min=1, max=100)])
    # No DataRequired: it rejects 0 before the Dutch messages in
    # validate_source_language_id / validate_target_language_id can run.
    source_language_id = SelectField("Brontaal", coerce=int)
    target_language_id = SelectField("Doeltaal", coerce=int)
    category_id = SelectField("Categorie", coerce=int)
    submit = SubmitField("Lijst Aanmaken")

    def __init__(self, languages=None, categories=None, *args, **kwargs):
        super(NewListForm, self).__init__(*args, **kwargs)
        if languages:
            lang_choices = [(0, "- Selecteer -")] + [
                (lang.id, lang.name) for lang in languages
            ]
            self.source_language_id.choices = lang_choices
            self.target_language_id.choices = lang_choices
        else:
            self.source_language_id.choices = []
            self.target_language_id.choices = []
        if categories:
            self.category_id.choices = [(0, "Geen categorie")] + [
                (cat.id, cat.name) for cat in categories
            ]
        else:
            self.category_id.choices = [(0, "Geen categorie")]

    def validate_source_language_id(self, field):
        """Validate that a source language is selected"""
        if field.data == 0:
            raise ValidationError("Selecteer een brontaal")

    def validate_target_language_id(self, field):
        """Validate that target language is selected and different from source"""
        if field.data == 0:
            raise ValidationError("Selecteer een doeltaal")
        if field.data == self.source_language_id.data:
            raise ValidationError("Bron- en doeltaal moeten verschillend zijn")


class LanguageFilterForm(FlaskForm):
    """Form voor het filteren van lijsten op taal"""

    language_id = SelectField("Filter op taal", coerce=int)

    def __init__(self, languages=None, *args, **kwargs):
        super(LanguageFilterForm, self).__init__(*args, **kwargs)
        if languages:
            self.language_id.choices = [(0, "Alle talen")] + [
                (lang.id, lang.name) for lang in languages
            ]
        else:
            self.language_id.choices = [(0, "Alle talen")]


class AddEntryForm(FlaskForm):
    """Form voor het toevoegen van een woord of zin"""

    entry_type = SelectField(
        "Type",
        choices=EntryType.choices(),
        validators=[DataRequired()],
    )
    source_word = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    target_word = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    pronunciation_note = StringField(
        "Uitspraak notitie (optioneel)", validators=[Length(max=200)]
    )
    submit = SubmitField("Toevoegen")


class EditEntryForm(FlaskForm):
    """Form voor het bewerken van een woord of zin"""

    entry_type = SelectField(
        "Type",
        choices=EntryType.choices(),
        validators=[DataRequired()],
    )
    source_word = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    target_word = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    pronunciation_note = StringField(
        "Uitspraak notitie (optioneel)", validators=[Length(max=200)]
    )
    submit = SubmitField("Bijwerken")


class DeleteForm(FlaskForm):
    """Form voor het verwijderen (alleen CSRF token)"""

    submit = SubmitField("Verwijderen")


class ImportSamplesForm(FlaskForm):
    """Form voor het importeren van de voorbeeldlijsten (alleen CSRF token)"""

    submit = SubmitField("Voorbeeldlijsten importeren")


class QuizAnswerForm(FlaskForm):
    """Form voor het beantwoorden van een quiz vraag"""

    answer = StringField("Jouw antwoord", validators=[DataRequired()])
    submit = SubmitField("Controleren")


class QuizDirectionForm(FlaskForm):
    """Form voor het kiezen van de quiz richting"""

    direction = SelectField(
        "Richting",
        validators=[DataRequired()],
    )
    submit = SubmitField("Start Quiz")

    def __init__(self, source_language=None, target_language=None, *args, **kwargs):
        super(QuizDirectionForm, self).__init__(*args, **kwargs)
        if source_language and target_language:
            self.direction.choices = [
                ("random", "Willekeurig (beide richtingen)"),
                ("forward", f"{source_language.name} → {target_language.name}"),
                ("reverse", f"{target_language.name} → {source_language.name}"),
            ]
        else:
            # Fallback voor als er geen talen zijn meegegeven
            self.direction.choices = [
                ("random", "Willekeurig (beide richtingen)"),
                ("forward", "Brontaal → Doeltaal"),
                ("reverse", "Doeltaal → Brontaal"),
            ]
