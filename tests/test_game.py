from datetime import date, timedelta

from app import db
from app.game import (
    XP_CORRECT,
    XP_PERFECT_QUIZ,
    XP_QUIZ_COMPLETED,
    XP_WRONG,
    _streaks,
    build_profile,
    current_combo,
    level_floor,
    level_for_xp,
    mastery,
    quiz_rewards,
)
from app.models import Entry, Language, List, QuizAnswer, QuizSession


def _make_entry():
    nl = Language(name="Dutch", code="nl")
    la = Language(name="Latin", code="la")
    word_list = List(name="Test", source_language=la, target_language=nl)
    entry = Entry(source_word="amare", target_word="liefhebben")
    word_list.entries.append(entry)
    db.session.add(word_list)
    db.session.commit()
    return entry


def _make_session(entry, results, status="completed"):
    quiz = QuizSession(
        quiz_type="single",
        direction="forward",
        total_questions=len(results),
        correct_answers=sum(results),
        status=status,
    )
    db.session.add(quiz)
    db.session.flush()
    for ok in results:
        db.session.add(
            QuizAnswer(
                session_id=quiz.id,
                entry_id=entry.id,
                user_answer="x",
                correct_answer="liefhebben",
                is_correct=ok,
                question_direction="forward",
            )
        )
    db.session.commit()
    return quiz


def test_levels():
    assert level_for_xp(0) == 1
    assert level_for_xp(level_floor(2) - 1) == 1
    assert level_for_xp(level_floor(2)) == 2
    assert level_for_xp(level_floor(5) + 1) == 5


def test_streaks():
    today = date(2026, 11, 14)
    day = timedelta(days=1)
    assert _streaks(set(), today) == (0, 0)
    # Practised yesterday and the day before, not yet today: streak still alive.
    assert _streaks({today - day, today - 2 * day}, today) == (2, 2)
    # Gap of two days breaks the current streak but not the longest one.
    old_run = {today - 10 * day, today - 9 * day, today - 8 * day}
    assert _streaks(old_run | {today}, today) == (1, 3)


def test_mastery():
    class E:
        def __init__(self, c, w):
            self.correct_count, self.incorrect_count = c, w

    assert mastery(E(0, 0)) == 0
    assert mastery(E(1, 3)) == 1
    assert mastery(E(3, 1)) == 2
    assert mastery(E(6, 1)) == 3


def test_profile_xp_and_rewards(app):
    entry = _make_entry()
    _make_session(entry, [True, False])
    perfect = _make_session(entry, [True] * 5)

    profile = build_profile()
    expected = 6 * XP_CORRECT + 1 * XP_WRONG + 2 * XP_QUIZ_COMPLETED + XP_PERFECT_QUIZ
    assert profile.xp == expected
    assert profile.quizzes == 2
    assert profile.streak == 1 and profile.practiced_today
    assert profile.today_correct == 6

    rewards = quiz_rewards(perfect.id)
    assert rewards["xp_gained"] == 5 * XP_CORRECT + XP_QUIZ_COMPLETED + XP_PERFECT_QUIZ
    new = {a.key for a in rewards["new_achievements"]}
    assert "perfect" in new
    assert "first_quiz" not in new  # already unlocked by the first quiz


def test_retried_mistakes_are_not_perfect(app):
    entry = _make_entry()
    # 5 questions, one answered wrong and then right on the retry.
    quiz = _make_session(entry, [True, True, False, True, True, True])
    quiz.total_questions = 5
    quiz.correct_answers = 5
    db.session.commit()

    profile = build_profile()
    assert profile.xp == 5 * XP_CORRECT + XP_WRONG + XP_QUIZ_COMPLETED
    assert "perfect" not in {a.key for a in profile.unlocked}


def test_combo(app):
    entry = _make_entry()
    quiz = _make_session(entry, [True, False, True, True], status="in_progress")
    assert current_combo(quiz.id) == 2
    assert current_combo(None) == 0


def test_profile_page(client):
    response = client.get("/profiel")
    assert response.status_code == 200
