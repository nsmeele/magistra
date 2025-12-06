from flask import Blueprint
from app.views import (
    IndexView,
    NewListView,
    ListDetailView,
    AddWordView,
    DeleteListView,
    DeleteWordView,
    QuizView,
    QuizAnswerView
)

# Create Blueprint
bp = Blueprint('main', __name__)

# Register class-based views
bp.add_url_rule('/', view_func=IndexView.as_view('index'))
bp.add_url_rule('/list/new', view_func=NewListView.as_view('new_list'))
bp.add_url_rule('/list/<int:list_id>', view_func=ListDetailView.as_view('list_detail'))
bp.add_url_rule('/list/<int:list_id>/word', view_func=AddWordView.as_view('add_word'))
bp.add_url_rule('/list/<int:list_id>/delete', view_func=DeleteListView.as_view('delete_list'))
bp.add_url_rule('/word/<int:word_id>/delete', view_func=DeleteWordView.as_view('delete_word'))
bp.add_url_rule('/list/<int:list_id>/quiz', view_func=QuizView.as_view('quiz'))
bp.add_url_rule('/list/<int:list_id>/quiz/answer', view_func=QuizAnswerView.as_view('quiz_answer'))
