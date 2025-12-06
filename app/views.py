from flask import render_template, request, redirect, url_for, flash, session
from flask.views import MethodView
from app.services import WordListService, QuizService


class IndexView(MethodView):
    """View for the homepage listing all word lists"""

    def __init__(self):
        self.list_service = WordListService()

    def get(self):
        """Display all word lists"""
        lists = self.list_service.get_all_lists()
        return render_template('index.html', lists=lists)


class NewListView(MethodView):
    """View for creating a new word list"""

    def __init__(self):
        self.list_service = WordListService()

    def get(self):
        """Display the new list form"""
        return render_template('new_list.html')

    def post(self):
        """Handle new list creation"""
        name = request.form.get('name')
        source_language = request.form.get('source_language')
        target_language = request.form.get('target_language')

        try:
            word_list = self.list_service.create_list(name, source_language, target_language)
            flash('Lijst aangemaakt!', 'success')
            return redirect(url_for('main.list_detail', list_id=word_list.id))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('new_list.html')


class ListDetailView(MethodView):
    """View for displaying list details and managing words"""

    def __init__(self):
        self.list_service = WordListService()

    def get(self, list_id):
        """Display list details with all words"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash('Lijst niet gevonden', 'error')
            return redirect(url_for('main.index'))
        return render_template('list_detail.html', word_list=word_list)


class AddWordView(MethodView):
    """View for adding a word to a list"""

    def __init__(self):
        self.list_service = WordListService()

    def post(self, list_id):
        """Add a new word to the list"""
        source_word = request.form.get('source_word')
        target_word = request.form.get('target_word')

        try:
            self.list_service.add_word_to_list(list_id, source_word, target_word)
            flash('Woord toegevoegd!', 'success')
        except ValueError as e:
            flash(str(e), 'error')

        return redirect(url_for('main.list_detail', list_id=list_id))


class DeleteListView(MethodView):
    """View for deleting a word list"""

    def __init__(self):
        self.list_service = WordListService()

    def post(self, list_id):
        """Delete the word list"""
        try:
            self.list_service.delete_list(list_id)
            flash('Lijst verwijderd', 'success')
        except ValueError as e:
            flash(str(e), 'error')

        return redirect(url_for('main.index'))


class DeleteWordView(MethodView):
    """View for deleting a word"""

    def __init__(self):
        self.list_service = WordListService()

    def post(self, word_id):
        """Delete the word"""
        try:
            list_id = self.list_service.delete_word(word_id)
            flash('Woord verwijderd', 'success')
            return redirect(url_for('main.list_detail', list_id=list_id))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('main.index'))


class QuizView(MethodView):
    """View for the quiz functionality"""

    def __init__(self):
        self.quiz_service = QuizService()
        self.list_service = WordListService()

    def get(self, list_id):
        """Display the current quiz question or results"""
        word_list = self.list_service.get_list_by_id(list_id)
        if not word_list:
            flash('Lijst niet gevonden', 'error')
            return redirect(url_for('main.index'))

        # Initialize quiz if needed
        if 'quiz_words' not in session or session.get('quiz_list_id') != list_id:
            try:
                quiz_data = self.quiz_service.initialize_quiz(list_id)
                session.update(quiz_data)
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('main.list_detail', list_id=list_id))

        # Check if quiz is complete
        if self.quiz_service.is_quiz_complete(session):
            results = self.quiz_service.get_quiz_results(session)
            # Clear session
            session.pop('quiz_words', None)
            session.pop('quiz_list_id', None)
            session.pop('quiz_index', None)
            session.pop('quiz_score', None)
            return render_template('quiz_complete.html',
                                 score=results['score'],
                                 total=results['total'],
                                 word_list=word_list)

        # Get current question
        word, progress = self.quiz_service.get_current_question(session)
        if not word:
            flash('Er is een fout opgetreden', 'error')
            return redirect(url_for('main.list_detail', list_id=list_id))

        return render_template('quiz.html',
                             word=word,
                             word_list=word_list,
                             progress=progress)


class QuizAnswerView(MethodView):
    """View for handling quiz answers"""

    def __init__(self):
        self.quiz_service = QuizService()

    def post(self, list_id):
        """Check the user's answer and advance quiz"""
        word_id = request.form.get('word_id', type=int)
        user_answer = request.form.get('answer', '')

        try:
            is_correct, correct_answer = self.quiz_service.check_answer(word_id, user_answer)

            # Get source word for flash message
            from app.repositories import WordRepository
            word_repo = WordRepository()
            word = word_repo.get_by_id(word_id)

            if is_correct:
                flash(f'Correct! {word.source_word} = {correct_answer}', 'success')
            else:
                flash(f'Fout! {word.source_word} = {correct_answer} (jij antwoordde: {user_answer})', 'error')

            # Advance quiz
            quiz_data = self.quiz_service.advance_quiz(dict(session), is_correct)
            session.update(quiz_data)

        except ValueError as e:
            flash(str(e), 'error')

        return redirect(url_for('main.quiz', list_id=list_id))
