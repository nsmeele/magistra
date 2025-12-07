from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class NewListForm(FlaskForm):
    """Form voor het aanmaken van een nieuwe lijst"""

    name = StringField("Naam", validators=[DataRequired(), Length(min=1, max=100)])
    source_language = StringField(
        "Brontaal", validators=[DataRequired(), Length(min=1, max=50)]
    )
    target_language = StringField(
        "Doeltaal", validators=[DataRequired(), Length(min=1, max=50)]
    )
    submit = SubmitField("Lijst Aanmaken")


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
