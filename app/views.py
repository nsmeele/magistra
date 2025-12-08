from flask import flash, redirect, render_template, request, session, url_for
from flask.views import MethodView

from app.ai_service import AIService
from app.forms import (
    AddEntryForm,
    AIGenerateForm,
    DeleteForm,
    EditEntryForm,
    LanguageFilterForm,
    NewListForm,
    QuizAnswerForm,
    QuizDirectionForm,
    SaveGeneratedListForm,
)
from app.services import CategoryService, LanguageService, ListService, QuizService


class IndexView(MethodView):
    """View for the homepage listing all lists"""

    def __init__(self):
        self.list_service = ListService()
        self.language_service = LanguageService()

    def get(self):
        """Display all word lists with optional language filter"""
        languages = self.language_service.get_all_languages()
        form = LanguageFilterForm(languages=languages)

        # Get filter from query parameter
        language_id = request.args.get("language_id", 0, type=int)
        selected_language = None
        if language_id:
            form.language_id.data = language_id
            selected_language = self.language_service.get_language_by_id(language_id)
            # Filter op language_name zodat zowel source als target taal matchen
            lists = self.list_service.get_all_lists(language=selected_language)
        else:
            lists = self.list_service.get_all_lists()

        return render_template(
            "index.html",
            lists=lists,
            form=form,
            languages=languages,
            selected_language=selected_language,
        )


class NewListView(MethodView):
    """View for creating a new list"""

    def __init__(self):
        self.list_service = ListService()
        self.language_service = LanguageService()
        self.category_service = CategoryService()

    def get(self):
        """Display the new list form"""
        languages = self.language_service.get_all_languages()
        categories = self.category_service.get_all_categories()
        form = NewListForm(languages=languages, categories=categories)
        return render_template("new_list.html", form=form)

    def post(self):
        """Handle new list creation"""
        languages = self.language_service.get_all_languages()
        categories = self.category_service.get_all_categories()
        form = NewListForm(languages=languages, categories=categories)

        if form.validate_on_submit():
            try:
                category_id = form.category_id.data if form.category_id.data else None
                word_list = self.list_service.create_list(
                    form.name.data,
                    form.source_language.data,
                    form.target_language.data,
                    category_id=category_id,
                )
                flash("Lijst aangemaakt!", "success")
                return redirect(url_for("main.list_detail", list_id=word_list.id))
            except ValueError as e:
                flash(str(e), "error")

        return render_template("new_list.html", form=form)


class EditListView(MethodView):
    def __init__(self):
        self.list_service = ListService()
        self.language_service = LanguageService()
        self.category_service = CategoryService()

    def get(self, list_id):
        """Display the edit list form"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        languages = self.language_service.get_all_languages()
        categories = self.category_service.get_all_categories()
        form = NewListForm(languages=languages, categories=categories, obj=word_list)
        return render_template("edit_list.html", form=form, word_list=word_list)


class ListDetailView(MethodView):
    """View for displaying list details and managing entries"""

    def __init__(self):
        self.list_service = ListService()

    def get(self, list_id):
        """Display list details with all words"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        form = AddEntryForm()
        delete_form = DeleteForm()
        return render_template(
            "list_detail.html", word_list=word_list, form=form, delete_form=delete_form
        )


class AddEntryView(MethodView):
    """View for adding an entry to a list"""

    def __init__(self):
        self.list_service = ListService()

    def post(self, list_id):
        """Add a new entry to the list"""
        form = AddEntryForm()

        if form.validate_on_submit():
            try:
                self.list_service.add_entry_to_list(
                    list_id,
                    form.source_word.data,
                    form.target_word.data,
                    form.entry_type.data,
                )
                flash("Item toegevoegd!", "success")
            except ValueError as e:
                flash(str(e), "error")

        return redirect(url_for("main.list_detail", list_id=list_id))


class EditEntryView(MethodView):
    """View for editing an entry"""

    def __init__(self):
        self.list_service = ListService()

    def get(self, entry_id):
        """Display the edit form"""
        entry = self.list_service.get_entry_by_id(entry_id)
        if not entry:
            flash("Item niet gevonden", "error")
            return redirect(url_for("main.index"))

        word_list = self.list_service.get_list_by_id(entry.list_id)
        form = EditEntryForm(obj=entry)
        return render_template(
            "edit_entry.html", entry=entry, word_list=word_list, form=form
        )

    def post(self, entry_id):
        """Update the entry"""
        entry = self.list_service.get_entry_by_id(entry_id)
        if not entry:
            flash("Item niet gevonden", "error")
            return redirect(url_for("main.index"))

        list_id = entry.list_id
        form = EditEntryForm()

        if form.validate_on_submit():
            try:
                self.list_service.update_entry(
                    entry_id,
                    form.source_word.data,
                    form.target_word.data,
                    form.entry_type.data,
                )
                flash("Item bijgewerkt!", "success")
                return redirect(url_for("main.list_detail", list_id=list_id))
            except ValueError as e:
                flash(str(e), "error")

        word_list = self.list_service.get_list_by_id(list_id)
        return render_template(
            "edit_entry.html", entry=entry, word_list=word_list, form=form
        )


class DeleteListView(MethodView):
    """View for deleting a list"""

    def __init__(self):
        self.list_service = ListService()

    def post(self, list_id):
        """Delete the word list"""
        try:
            self.list_service.delete_list(list_id)
            flash("Lijst verwijderd", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("main.index"))


class DeleteEntryView(MethodView):
    """View for deleting an entry"""

    def __init__(self):
        self.list_service = ListService()

    def post(self, entry_id):
        """Delete the entry"""
        try:
            list_id = self.list_service.delete_entry(entry_id)
            flash("Item verwijderd", "success")
            return redirect(url_for("main.list_detail", list_id=list_id))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("main.index"))


class QuizStartView(MethodView):
    """View for starting a quiz with direction selection"""

    def __init__(self):
        self.quiz_service = QuizService()
        self.list_service = ListService()

    def get(self, list_id):
        """Display the quiz start page with direction selection"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        if not word_list.entries:
            flash("Deze lijst heeft geen items om te oefenen", "error")
            return redirect(url_for("main.list_detail", list_id=list_id))

        form = QuizDirectionForm(
            source_language=word_list.source_language,
            target_language=word_list.target_language,
        )
        return render_template("quiz_start.html", form=form, word_list=word_list)

    def post(self, list_id):
        """Start the quiz with the selected direction"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        form = QuizDirectionForm(
            source_language=word_list.source_language,
            target_language=word_list.target_language,
        )
        if form.validate_on_submit():
            direction = form.direction.data
            try:
                quiz_data = self.quiz_service.initialize_quiz(list_id, direction)
                quiz_data["direction"] = direction  # Store direction for history
                quiz_data["quiz_answers"] = []  # Track all answers

                # Create quiz session in database
                quiz_session = self.quiz_service.create_or_update_session(quiz_data)
                quiz_data["quiz_session_id"] = quiz_session.id

                session.update(quiz_data)
                return redirect(url_for("main.quiz", list_id=list_id))
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("main.list_detail", list_id=list_id))

        return render_template("quiz_start.html", form=form, word_list=word_list)


class QuizView(MethodView):
    """View for the quiz functionality"""

    def __init__(self):
        self.quiz_service = QuizService()
        self.list_service = ListService()

    def get(self, list_id):
        """Display the current quiz question or results"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        # Debug logging
        print(
            f"DEBUG: Session before init: quiz_questions={session.get('quiz_questions')}, quiz_list_id={session.get('quiz_list_id')}, quiz_index={session.get('quiz_index')}"
        )

        # Check if quiz needs initialization (redirect to quiz start if needed)
        if "quiz_questions" not in session or session.get("quiz_list_id") != list_id:
            return redirect(url_for("main.quiz_start", list_id=list_id))

        # Check if quiz is complete
        if self.quiz_service.is_quiz_complete(session):
            results = self.quiz_service.get_quiz_results(session)

            # Mark session as complete
            quiz_session_id = session.get("quiz_session_id")
            if quiz_session_id:
                try:
                    self.quiz_service.complete_quiz_session(
                        quiz_session_id, results["score"]
                    )
                except Exception as e:
                    print(f"Error completing quiz session: {e}")
            else:
                # Fallback: save legacy way if no session ID
                quiz_answers = session.get("quiz_answers", [])
                if quiz_answers:
                    try:
                        self.quiz_service.save_quiz_session(dict(session), quiz_answers)
                    except Exception as e:
                        print(f"Error saving quiz session: {e}")

            # Clear session
            session.pop("quiz_questions", None)
            session.pop("quiz_list_id", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
            session.pop("quiz_answers", None)
            session.pop("direction", None)
            session.pop("quiz_session_id", None)
            return render_template(
                "quiz_complete.html",
                score=results["score"],
                total=results["total"],
                word_list=word_list,
            )

        # Get current question
        print(f"DEBUG: Getting current question with session: {dict(session)}")
        entry, updated_quiz_data, progress, direction = (
            self.quiz_service.get_current_question(dict(session))
        )
        print(f"DEBUG: Entry: {entry}, progress: {progress}, direction: {direction}")
        if not entry:
            # All entries were deleted or quiz is broken, reinitialize
            session.pop("quiz_questions", None)
            session.pop("quiz_list_id", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
            flash(
                "De quiz kon niet worden geladen. Sommige items zijn mogelijk verwijderd. Probeer opnieuw.",
                "error",
            )
            return redirect(url_for("main.list_detail", list_id=list_id))

        # Update session with potentially skipped indices
        session.update(updated_quiz_data)

        form = QuizAnswerForm()
        return render_template(
            "quiz.html",
            entry=entry,
            word_list=word_list,
            progress=progress,
            direction=direction,
            form=form,
        )


class QuizAnswerView(MethodView):
    """View for handling quiz answers"""

    def __init__(self):
        self.quiz_service = QuizService()

    def post(self, list_id):
        """Check the user's answer and advance quiz"""
        form = QuizAnswerForm()

        if form.validate_on_submit():
            entry_id = request.form.get("entry_id", type=int)
            direction = request.form.get("direction", "forward")
            user_answer = form.answer.data

            try:
                is_correct, correct_answer = self.quiz_service.check_answer(
                    entry_id, user_answer, direction
                )

                # Get entry for flash message
                from app.repositories import EntryRepository

                entry_repo = EntryRepository()
                entry = entry_repo.get_by_id(entry_id)

                # Show the question word based on direction
                question_word = (
                    entry.source_word if direction == "forward" else entry.target_word
                )

                if is_correct:
                    flash(f"Correct! {question_word} = {correct_answer}", "success")
                else:
                    flash(
                        f"Fout! {question_word} = {correct_answer} (jij antwoordde: {user_answer})",
                        "error",
                    )

                # Track answer for history
                answer_data = {
                    "entry_id": entry_id,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "direction": direction,
                }

                # Save answer to database if we have a session ID
                quiz_session_id = session.get("quiz_session_id")
                if quiz_session_id:
                    try:
                        self.quiz_service.save_quiz_answer(quiz_session_id, answer_data)
                    except Exception as e:
                        print(f"Error saving answer: {e}")

                # Also keep in session for legacy/fallback
                quiz_answers = session.get("quiz_answers", [])
                quiz_answers.append(answer_data)
                session["quiz_answers"] = quiz_answers

                # Advance quiz and update session in DB
                quiz_data = self.quiz_service.advance_quiz(dict(session), is_correct)
                session.update(quiz_data)

                # Update quiz session progress
                if quiz_session_id:
                    try:
                        self.quiz_service.create_or_update_session(
                            dict(session), quiz_session_id
                        )
                    except Exception as e:
                        print(f"Error updating session: {e}")

            except ValueError as e:
                flash(str(e), "error")

        return redirect(url_for("main.quiz", list_id=list_id))


class MixedQuizView(MethodView):
    """View for selecting lists for a mixed quiz"""

    def __init__(self):
        self.list_service = ListService()

    def get(self):
        """Display list selection page grouped by language pairs"""
        all_lists = self.list_service.get_all_lists()

        # Group lists by language pair
        language_pairs = {}
        for lst in all_lists:
            key = f"{lst.source_language.name} → {lst.target_language.name}"
            if key not in language_pairs:
                language_pairs[key] = []
            language_pairs[key].append(lst)

        return render_template("mixed_quiz.html", language_pairs=language_pairs)


class MixedQuizStartView(MethodView):
    """View for starting a mixed quiz with selected lists"""

    def __init__(self):
        self.quiz_service = QuizService()

    def post(self):
        """Start a mixed quiz with selected lists"""
        # Get selected list IDs and direction from form
        selected_list_ids = request.form.getlist("list_ids", type=int)
        direction = request.form.get("direction", "random")

        if not selected_list_ids:
            flash("Selecteer minimaal één lijst", "error")
            return redirect(url_for("main.mixed_quiz"))

        try:
            # Initialize mixed quiz with direction preference
            quiz_data = self.quiz_service.initialize_mixed_quiz(
                selected_list_ids, direction
            )
            quiz_data["direction"] = direction  # Store direction for history
            quiz_data["quiz_answers"] = []  # Track all answers

            # Create quiz session in database
            quiz_session = self.quiz_service.create_or_update_session(quiz_data)
            quiz_data["quiz_session_id"] = quiz_session.id

            session.update(quiz_data)
            flash(f"Quiz gestart met {len(selected_list_ids)} lijst(en)!", "success")
            return redirect(url_for("main.mixed_quiz_question"))

        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("main.mixed_quiz"))


class MixedQuizQuestionView(MethodView):
    """View for displaying mixed quiz questions"""

    def __init__(self):
        self.quiz_service = QuizService()

    def get(self):
        """Display the current quiz question or results"""
        # Check if there's an active mixed quiz
        if "quiz_list_ids" not in session or "quiz_questions" not in session:
            flash("Geen actieve quiz. Start een nieuwe quiz.", "error")
            return redirect(url_for("main.mixed_quiz"))

        # Check if quiz is complete
        if self.quiz_service.is_quiz_complete(session):
            results = self.quiz_service.get_quiz_results(session)
            list_names = session.get("quiz_list_names", [])

            # Mark session as complete
            quiz_session_id = session.get("quiz_session_id")
            if quiz_session_id:
                try:
                    self.quiz_service.complete_quiz_session(
                        quiz_session_id, results["score"]
                    )
                except Exception as e:
                    print(f"Error completing quiz session: {e}")
            else:
                # Fallback: save legacy way if no session ID
                quiz_answers = session.get("quiz_answers", [])
                if quiz_answers:
                    try:
                        self.quiz_service.save_quiz_session(dict(session), quiz_answers)
                    except Exception as e:
                        print(f"Error saving quiz session: {e}")

            # Clear session
            session.pop("quiz_questions", None)
            session.pop("quiz_list_ids", None)
            session.pop("quiz_list_names", None)
            session.pop("quiz_source_language", None)
            session.pop("quiz_target_language", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
            session.pop("quiz_answers", None)
            session.pop("direction", None)
            session.pop("quiz_session_id", None)
            return render_template(
                "mixed_quiz_complete.html",
                score=results["score"],
                total=results["total"],
                list_names=list_names,
            )

        # Get current question
        entry, updated_quiz_data, progress, direction = (
            self.quiz_service.get_current_question(dict(session))
        )
        if not entry:
            # All entries were deleted or quiz is broken, clear session
            session.pop("quiz_questions", None)
            session.pop("quiz_list_ids", None)
            session.pop("quiz_list_names", None)
            session.pop("quiz_source_language", None)
            session.pop("quiz_target_language", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
            flash("De quiz kon niet worden geladen. Probeer opnieuw.", "error")
            return redirect(url_for("main.mixed_quiz"))

        # Update session
        session.update(updated_quiz_data)

        form = QuizAnswerForm()
        list_names = session.get("quiz_list_names", [])
        return render_template(
            "mixed_quiz_question.html",
            entry=entry,
            progress=progress,
            direction=direction,
            list_names=list_names,
            form=form,
        )


class MixedQuizAnswerView(MethodView):
    """View for handling mixed quiz answers"""

    def __init__(self):
        self.quiz_service = QuizService()

    def post(self):
        """Check the user's answer and advance quiz"""
        form = QuizAnswerForm()

        if form.validate_on_submit():
            entry_id = request.form.get("entry_id", type=int)
            direction = request.form.get("direction", "forward")
            user_answer = form.answer.data

            try:
                is_correct, correct_answer = self.quiz_service.check_answer(
                    entry_id, user_answer, direction
                )

                # Get entry for flash message
                from app.repositories import EntryRepository

                entry_repo = EntryRepository()
                entry = entry_repo.get_by_id(entry_id)

                # Show the question word based on direction
                question_word = (
                    entry.source_word if direction == "forward" else entry.target_word
                )

                if is_correct:
                    flash(f"Correct! {question_word} = {correct_answer}", "success")
                else:
                    flash(
                        f"Fout! {question_word} = {correct_answer} (jij antwoordde: {user_answer})",
                        "error",
                    )

                # Track answer for history
                answer_data = {
                    "entry_id": entry_id,
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "direction": direction,
                }

                # Save answer to database if we have a session ID
                quiz_session_id = session.get("quiz_session_id")
                if quiz_session_id:
                    try:
                        self.quiz_service.save_quiz_answer(quiz_session_id, answer_data)
                    except Exception as e:
                        print(f"Error saving answer: {e}")

                # Also keep in session for legacy/fallback
                quiz_answers = session.get("quiz_answers", [])
                quiz_answers.append(answer_data)
                session["quiz_answers"] = quiz_answers

                # Advance quiz and update session in DB
                quiz_data = self.quiz_service.advance_quiz(dict(session), is_correct)
                session.update(quiz_data)

                # Update quiz session progress
                if quiz_session_id:
                    try:
                        self.quiz_service.create_or_update_session(
                            dict(session), quiz_session_id
                        )
                    except Exception as e:
                        print(f"Error updating session: {e}")

            except ValueError as e:
                flash(str(e), "error")

        return redirect(url_for("main.mixed_quiz_question"))


class QuizHistoryView(MethodView):
    """View for quiz history listing"""

    def __init__(self):
        self.quiz_service = QuizService()

    def get(self):
        """Display quiz history with trends"""
        sessions = self.quiz_service.get_quiz_history()
        incomplete_sessions = self.quiz_service.get_incomplete_sessions()
        return render_template(
            "quiz_history.html",
            sessions=sessions,
            incomplete_sessions=incomplete_sessions,
        )


class QuizHistoryDetailView(MethodView):
    """View for detailed quiz session review"""

    def __init__(self):
        self.quiz_service = QuizService()

    def get(self, session_id):
        """Display detailed quiz session with all answers"""
        quiz_session = self.quiz_service.get_quiz_session_detail(session_id)
        if not quiz_session:
            flash("Quiz sessie niet gevonden", "error")
            return redirect(url_for("main.quiz_history"))

        return render_template("quiz_history_detail.html", quiz_session=quiz_session)


class ResumeQuizView(MethodView):
    """View for resuming an incomplete quiz"""

    def __init__(self):
        self.quiz_service = QuizService()

    def get(self, session_id):
        """Resume a quiz session"""
        quiz_session = self.quiz_service.get_quiz_session_detail(session_id)

        if not quiz_session:
            flash("Quiz sessie niet gevonden", "error")
            return redirect(url_for("main.quiz_history"))

        if quiz_session.status != "in_progress":
            flash("Deze quiz is al voltooid", "info")
            return redirect(url_for("main.quiz_history_detail", session_id=session_id))

        # Restore quiz state from database
        if not quiz_session.quiz_data:
            flash("Kan quiz niet hervatten: geen opgeslagen data", "error")
            return redirect(url_for("main.quiz_history"))

        # Load quiz data into session
        session.update(quiz_session.quiz_data)
        session["quiz_session_id"] = quiz_session.id

        # Determine redirect based on quiz type
        if quiz_session.quiz_type == "mixed":
            flash("Quiz hervat!", "success")
            return redirect(url_for("main.mixed_quiz_question"))
        else:
            # Get list_id from session_lists
            if quiz_session.session_lists:
                list_id = quiz_session.session_lists[0].list_id
                flash("Quiz hervat!", "success")
                return redirect(url_for("main.quiz", list_id=list_id))

        flash("Kan quiz niet hervatten", "error")
        return redirect(url_for("main.quiz_history"))


class SmartPracticeView(MethodView):
    """View for smart practice quiz with difficult words"""

    def __init__(self):
        self.quiz_service = QuizService()
        self.list_service = ListService()

    def get(self, list_id=None):
        """Display smart practice start page"""
        difficult_entries = self.quiz_service.get_difficult_entries(
            list_id=list_id, limit=15
        )

        if not difficult_entries:
            flash("Geen moeilijke woorden gevonden. Oefen eerst wat meer!", "info")
            if list_id:
                return redirect(url_for("main.list_detail", list_id=list_id))
            return redirect(url_for("main.index"))

        # Get the list if specific
        word_list = None
        if list_id:
            word_list = self.list_service.get_list_by_id(list_id)

        return render_template(
            "smart_practice.html",
            entries=difficult_entries,
            word_list=word_list,
        )

    def post(self, list_id=None):
        """Start smart practice quiz"""
        difficult_entries = self.quiz_service.get_difficult_entries(
            list_id=list_id, limit=15
        )

        if not difficult_entries:
            flash("Geen moeilijke woorden gevonden.", "error")
            return redirect(url_for("main.index"))

        # Create quiz questions from difficult entries
        direction = request.form.get("direction", "random")
        quiz_questions = []
        for entry in difficult_entries:
            if direction == "random":
                entry_direction = (
                    "forward"
                    if entry.success_rate and entry.success_rate < 50
                    else "reverse"
                )
            else:
                entry_direction = direction
            quiz_questions.append({"entry_id": entry.id, "direction": entry_direction})

        # Shuffle for variety
        import random

        random.shuffle(quiz_questions)

        # Store in session
        quiz_data = {
            "quiz_questions": quiz_questions,
            "quiz_index": 0,
            "quiz_score": 0,
            "quiz_total": len(quiz_questions),
            "quiz_answers": [],
            "direction": direction,
        }

        if list_id:
            quiz_data["quiz_list_id"] = list_id
            session.update(quiz_data)
            flash("Smart practice quiz gestart!", "success")
            return redirect(url_for("main.quiz", list_id=list_id))
        else:
            # Mixed quiz mode for smart practice across all lists
            list_ids = list(set(entry.list_id for entry in difficult_entries))
            quiz_data["quiz_list_ids"] = list_ids
            quiz_data["quiz_list_names"] = [
                self.list_service.get_list_by_id(lid).name for lid in list_ids
            ]
            session.update(quiz_data)
            flash("Smart practice quiz gestart!", "success")
            return redirect(url_for("main.mixed_quiz_question"))


class AIGenerateView(MethodView):
    """View for AI-powered list generation"""

    def __init__(self):
        self.ai_service = AIService()
        self.list_service = ListService()
        self.language_service = LanguageService()

    def get(self):
        """Display the AI generation form"""
        providers = self.ai_service.get_available_providers()
        languages = self.language_service.get_all_languages()
        available_providers = [p for p in providers if p["available"]]

        if not available_providers:
            flash(
                "Geen AI providers beschikbaar. Configureer een API key of start Ollama.",
                "error",
            )
            return render_template(
                "ai_generate.html", form=None, providers=providers, generated_items=None
            )

        form = AIGenerateForm(providers=providers, languages=languages)
        return render_template(
            "ai_generate.html", form=form, providers=providers, generated_items=None
        )

    def post(self):
        """Handle AI generation request"""
        providers = self.ai_service.get_available_providers()
        languages = self.language_service.get_all_languages()
        form = AIGenerateForm(providers=providers, languages=languages)

        if form.validate_on_submit():
            try:
                count = int(form.count.data) if form.count.data else None
                items = self.ai_service.generate_list(
                    provider_key=form.provider.data,
                    topic=form.topic.data,
                    source_language=form.source_language.data,
                    target_language=form.target_language.data,
                    entry_type=form.entry_type.data,
                    count=count,
                )

                # Store generated items in session for saving
                session["ai_generated_items"] = items
                session["ai_generated_meta"] = {
                    "topic": form.topic.data,
                    "source_language": form.source_language.data,
                    "target_language": form.target_language.data,
                    "entry_type": form.entry_type.data,
                }

                save_form = SaveGeneratedListForm()
                save_form.list_name.data = form.topic.data

                flash(f"{len(items)} items gegenereerd!", "success")
                return render_template(
                    "ai_generate.html",
                    form=form,
                    providers=providers,
                    generated_items=items,
                    save_form=save_form,
                    meta=session["ai_generated_meta"],
                )

            except Exception as e:
                flash(f"Fout bij genereren: {str(e)}", "error")

        return render_template(
            "ai_generate.html", form=form, providers=providers, generated_items=None
        )


class AISaveListView(MethodView):
    """View for saving AI-generated list"""

    def __init__(self):
        self.list_service = ListService()

    def post(self):
        """Save the generated items as a new list"""
        form = SaveGeneratedListForm()

        if not form.validate_on_submit():
            flash("Ongeldige invoer", "error")
            return redirect(url_for("main.ai_generate"))

        items = session.get("ai_generated_items")
        meta = session.get("ai_generated_meta")

        if not items or not meta:
            flash("Geen gegenereerde items om op te slaan", "error")
            return redirect(url_for("main.ai_generate"))

        # Get selected items from form
        selected_indices = request.form.getlist("selected_items")
        if selected_indices:
            # Filter to only selected items
            selected_indices = [int(i) for i in selected_indices]
            items = [items[i] for i in selected_indices if i < len(items)]

        if not items:
            flash("Selecteer minimaal 1 item om op te slaan", "error")
            return redirect(url_for("main.ai_generate"))

        try:
            # Create the list
            word_list = self.list_service.create_list(
                form.list_name.data,
                meta["source_language"],
                meta["target_language"],
            )

            # Add all items
            for item in items:
                self.list_service.add_entry_to_list(
                    word_list.id,
                    item["source"],
                    item["target"],
                    meta["entry_type"],
                )

            # Clear session
            session.pop("ai_generated_items", None)
            session.pop("ai_generated_meta", None)

            flash(
                f"Lijst '{form.list_name.data}' aangemaakt met {len(items)} items!",
                "success",
            )
            return redirect(url_for("main.list_detail", list_id=word_list.id))

        except Exception as e:
            flash(f"Fout bij opslaan: {str(e)}", "error")
            return redirect(url_for("main.ai_generate"))
