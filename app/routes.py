from flask import Blueprint
from app.views import (
    IndexView,
    NewListView,
    ListDetailView,
    AddEntryView,
    EditEntryView,
    DeleteListView,
    DeleteEntryView,
    QuizView,
    QuizAnswerView
)

# Create Blueprint
bp = Blueprint('main', __name__)

# Register class-based views
bp.add_url_rule('/', view_func=IndexView.as_view('index'))
bp.add_url_rule('/list/new', view_func=NewListView.as_view('new_list'))
bp.add_url_rule('/list/<int:list_id>', view_func=ListDetailView.as_view('list_detail'))
bp.add_url_rule('/list/<int:list_id>/entry', view_func=AddEntryView.as_view('add_entry'))
bp.add_url_rule('/entry/<int:entry_id>/edit', view_func=EditEntryView.as_view('edit_entry'), methods=['GET', 'POST'])
bp.add_url_rule('/list/<int:list_id>/delete', view_func=DeleteListView.as_view('delete_list'))
bp.add_url_rule('/entry/<int:entry_id>/delete', view_func=DeleteEntryView.as_view('delete_entry'))
bp.add_url_rule('/list/<int:list_id>/quiz', view_func=QuizView.as_view('quiz'))
bp.add_url_rule('/list/<int:list_id>/quiz/answer', view_func=QuizAnswerView.as_view('quiz_answer'))
