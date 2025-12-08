from flask import Blueprint

from app.views import (AddEntryView, DeleteEntryView, DeleteListView,
                       EditEntryView, EditListView, IndexView, ListDetailView,
                       MixedQuizAnswerView, MixedQuizQuestionView,
                       MixedQuizStartView, MixedQuizView, NewListView,
                       QuizAnswerView, QuizHistoryDetailView, QuizHistoryView,
                       QuizStartView, QuizView, ResumeQuizView,
                       SmartPracticeView)

# Create Blueprint
bp = Blueprint("main", __name__)

# Register class-based views
bp.add_url_rule("/", view_func=IndexView.as_view("index"))
bp.add_url_rule("/list/new", view_func=NewListView.as_view("new_list"))
bp.add_url_rule("/list/<int:list_id>", view_func=ListDetailView.as_view("list_detail"))
bp.add_url_rule(
    "/list/<int:list_id>/edit",
    view_func=EditListView.as_view("edit_list"),
    methods=["GET", "POST"],
)
bp.add_url_rule(
    "/list/<int:list_id>/entry", view_func=AddEntryView.as_view("add_entry")
)
bp.add_url_rule(
    "/entry/<int:entry_id>/edit",
    view_func=EditEntryView.as_view("edit_entry"),
    methods=["GET", "POST"],
)
bp.add_url_rule(
    "/list/<int:list_id>/delete", view_func=DeleteListView.as_view("delete_list")
)
bp.add_url_rule(
    "/entry/<int:entry_id>/delete", view_func=DeleteEntryView.as_view("delete_entry")
)
bp.add_url_rule(
    "/list/<int:list_id>/quiz/start",
    view_func=QuizStartView.as_view("quiz_start"),
    methods=["GET", "POST"],
)
bp.add_url_rule("/list/<int:list_id>/quiz", view_func=QuizView.as_view("quiz"))
bp.add_url_rule(
    "/list/<int:list_id>/quiz/answer", view_func=QuizAnswerView.as_view("quiz_answer")
)

# Mixed quiz routes
bp.add_url_rule("/quiz/mixed", view_func=MixedQuizView.as_view("mixed_quiz"))
bp.add_url_rule(
    "/quiz/mixed/start",
    view_func=MixedQuizStartView.as_view("mixed_quiz_start"),
    methods=["POST"],
)
bp.add_url_rule(
    "/quiz/mixed/question",
    view_func=MixedQuizQuestionView.as_view("mixed_quiz_question"),
)
bp.add_url_rule(
    "/quiz/mixed/answer",
    view_func=MixedQuizAnswerView.as_view("mixed_quiz_answer"),
    methods=["POST"],
)

# Quiz history routes
bp.add_url_rule("/quiz/history", view_func=QuizHistoryView.as_view("quiz_history"))
bp.add_url_rule(
    "/quiz/history/<int:session_id>",
    view_func=QuizHistoryDetailView.as_view("quiz_history_detail"),
)
bp.add_url_rule(
    "/quiz/resume/<int:session_id>",
    view_func=ResumeQuizView.as_view("resume_quiz"),
)

# Smart practice routes
bp.add_url_rule(
    "/quiz/practice",
    view_func=SmartPracticeView.as_view("smart_practice"),
    methods=["GET", "POST"],
)
bp.add_url_rule(
    "/list/<int:list_id>/practice",
    view_func=SmartPracticeView.as_view("smart_practice_list"),
    methods=["GET", "POST"],
)
