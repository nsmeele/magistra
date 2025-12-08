from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class NewListForm(FlaskForm):
    """Form voor het aanmaken van een nieuwe lijst"""

    name = StringField("Naam", validators=[DataRequired(), Length(min=1, max=100)])
    language_id = SelectField("Taal", coerce=int, validators=[DataRequired()])
    category_id = SelectField("Categorie", coerce=int)
    source_language = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=50)]
    )
    target_language = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=50)]
    )
    submit = SubmitField("Lijst Aanmaken")

    def __init__(self, languages=None, categories=None, *args, **kwargs):
        super(NewListForm, self).__init__(*args, **kwargs)
        if languages:
            self.language_id.choices = [(lang.id, lang.name) for lang in languages]
        else:
            self.language_id.choices = []
        if categories:
            self.category_id.choices = [(0, "Geen categorie")] + [
                (cat.id, cat.name) for cat in categories
            ]
        else:
            self.category_id.choices = [(0, "Geen categorie")]


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
        choices=[("word", "Woord"), ("sentence", "Zin")],
        validators=[DataRequired()],
    )
    source_word = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    target_word = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    submit = SubmitField("Toevoegen")


class EditEntryForm(FlaskForm):
    """Form voor het bewerken van een woord of zin"""

    entry_type = SelectField(
        "Type",
        choices=[("word", "Woord"), ("sentence", "Zin")],
        validators=[DataRequired()],
    )
    source_word = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    target_word = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=500)]
    )
    submit = SubmitField("Bijwerken")


class DeleteForm(FlaskForm):
    """Form voor het verwijderen (alleen CSRF token)"""

    submit = SubmitField("Verwijderen")


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
                ("forward", f"{source_language} → {target_language}"),
                ("reverse", f"{target_language} → {source_language}"),
            ]
        else:
            # Fallback voor als er geen talen zijn meegegeven
            self.direction.choices = [
                ("random", "Willekeurig (beide richtingen)"),
                ("forward", "Brontaal → Doeltaal"),
                ("reverse", "Doeltaal → Brontaal"),
            ]


class AIGenerateForm(FlaskForm):
    """Form voor het genereren van een lijst met AI"""

    provider = SelectField(
        "AI Provider",
        validators=[DataRequired()],
    )
    topic = StringField(
        "Onderwerp",
        validators=[DataRequired(), Length(min=1, max=200)],
    )
    entry_type = SelectField(
        "Type",
        choices=[("word", "Woorden"), ("sentence", "Zinnen")],
        validators=[DataRequired()],
    )
    source_language = StringField(
        "Brontaal",
        validators=[DataRequired(), Length(min=1, max=50)],
    )
    target_language = StringField(
        "Doeltaal",
        validators=[DataRequired(), Length(min=1, max=50)],
    )
    count = SelectField(
        "Aantal items",
        choices=[
            ("", "Automatisch"),
            ("5", "5"),
            ("10", "10"),
            ("15", "15"),
            ("20", "20"),
        ],
        default="10",
    )
    submit = SubmitField("Genereer Lijst")

    def __init__(self, providers=None, *args, **kwargs):
        super(AIGenerateForm, self).__init__(*args, **kwargs)
        if providers:
            self.provider.choices = [
                (p["key"], p["name"]) for p in providers if p["available"]
            ]
        else:
            self.provider.choices = []


class SaveGeneratedListForm(FlaskForm):
    """Form voor het opslaan van een gegenereerde lijst"""

    list_name = StringField(
        "Lijstnaam",
        validators=[DataRequired(), Length(min=1, max=100)],
    )
    submit = SubmitField("Opslaan als Nieuwe Lijst")
