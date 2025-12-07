from flask import flash, redirect, render_template, request, session, url_for
from flask.views import MethodView

from app.forms import (
    AddEntryForm,
    DeleteForm,
    EditEntryForm,
    NewListForm,
    QuizAnswerForm,
)
from app.services import ListService, QuizService


class IndexView(MethodView):
    """View for the homepage listing all lists"""

    def __init__(self):
        self.list_service = ListService()

    def get(self):
        """Display all word lists"""
        lists = self.list_service.get_all_lists()
        return render_template("index.html", lists=lists)


class NewListView(MethodView):
    """View for creating a new list"""

    def __init__(self):
        self.list_service = ListService()

    def get(self):
        """Display the new list form"""
        form = NewListForm()
        return render_template("new_list.html", form=form)

    def post(self):
        """Handle new list creation"""
        form = NewListForm()

        if form.validate_on_submit():
            try:
                word_list = self.list_service.create_list(
                    form.name.data, form.source_language.data, form.target_language.data
                )
                flash("Lijst aangemaakt!", "success")
                return redirect(url_for("main.list_detail", list_id=word_list.id))
            except ValueError as e:
                flash(str(e), "error")

        return render_template("new_list.html", form=form)


class EditListView(MethodView):
    def __init__(self):
        self.list_service = ListService()

    def get(self, list_id):
        """Display the edit list form"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash("Lijst niet gevonden", "error")
            return redirect(url_for("main.index"))

        form = NewListForm(obj=word_list)
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

        # Initialize quiz if needed
        if "quiz_questions" not in session or session.get("quiz_list_id") != list_id:
            print(f"DEBUG: Initializing quiz for list_id={list_id}")
            try:
                quiz_data = self.quiz_service.initialize_quiz(list_id)
                print(f"DEBUG: Quiz data from initialize: {quiz_data}")
                session.update(quiz_data)
                print(f"DEBUG: Session after init: {dict(session)}")
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("main.list_detail", list_id=list_id))

        # Check if quiz is complete
        if self.quiz_service.is_quiz_complete(session):
            results = self.quiz_service.get_quiz_results(session)
            # Clear session
            session.pop("quiz_questions", None)
            session.pop("quiz_list_id", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
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

                # Advance quiz
                quiz_data = self.quiz_service.advance_quiz(dict(session), is_correct)
                session.update(quiz_data)

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
            key = f"{lst.source_language} → {lst.target_language}"
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
        # Get selected list IDs from form
        selected_list_ids = request.form.getlist("list_ids", type=int)

        if not selected_list_ids:
            flash("Selecteer minimaal één lijst", "error")
            return redirect(url_for("main.mixed_quiz"))

        try:
            # Initialize mixed quiz
            quiz_data = self.quiz_service.initialize_mixed_quiz(selected_list_ids)
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
            # Clear session
            session.pop("quiz_questions", None)
            session.pop("quiz_list_ids", None)
            session.pop("quiz_list_names", None)
            session.pop("quiz_source_language", None)
            session.pop("quiz_target_language", None)
            session.pop("quiz_index", None)
            session.pop("quiz_score", None)
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

                # Advance quiz
                quiz_data = self.quiz_service.advance_quiz(dict(session), is_correct)
                session.update(quiz_data)

            except ValueError as e:
                flash(str(e), "error")

        return redirect(url_for("main.mixed_quiz_question"))
