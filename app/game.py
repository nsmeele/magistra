"""Game layer: XP, levels, daily streak, daily goal, achievements and word mastery.

Everything is derived from QuizAnswer / QuizSession / Entry, so there is no extra
state to keep in sync. Dates use the server's UTC dates.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func

from app import db
from app.models import Entry, QuizAnswer, QuizSession, utcnow

# --- Rules -----------------------------------------------------------------

XP_CORRECT = 10
XP_WRONG = 1
XP_QUIZ_COMPLETED = 25
XP_PERFECT_QUIZ = 50
PERFECT_MIN_QUESTIONS = 5
DAILY_GOAL = 20  # correct answers per day

# Latin ranks, one per level. Beyond the last one you stay "Magistra".
LEVEL_TITLES = [
    "Discipulus",
    "Tiro",
    "Lector",
    "Scriba",
    "Grammaticus",
    "Orator",
    "Rhetor",
    "Philosophus",
    "Doctor",
    "Magistra",
]

MASTERY_LEVELS = [
    (0, "Nieuw"),
    (1, "Lerend"),
    (2, "Bekend"),
    (3, "Beheerst"),
]


def level_floor(level: int) -> int:
    """Total XP needed to reach `level` (level 1 starts at 0)."""
    return 50 * level * (level - 1)


def level_for_xp(xp: int) -> int:
    level = 1
    while xp >= level_floor(level + 1):
        level += 1
    return level


def level_title(level: int) -> str:
    return LEVEL_TITLES[min(level, len(LEVEL_TITLES)) - 1]


def mastery(entry) -> int:
    """0 = nieuw, 1 = lerend, 2 = bekend, 3 = beheerst."""
    correct = entry.correct_count or 0
    wrong = entry.incorrect_count or 0
    total = correct + wrong
    if total == 0 or correct == 0:
        return 0
    rate = correct / total
    if correct >= 5 and rate >= 0.85:
        return 3
    if correct >= 3 and rate >= 0.6:
        return 2
    return 1


def mastery_label(value: int) -> str:
    return MASTERY_LEVELS[value][1]


# --- Achievements ----------------------------------------------------------


@dataclass
class Achievement:
    key: str
    title: str
    description: str
    icon: str  # FontAwesome solid icon name without "fa-"
    current: int
    target: int

    @property
    def unlocked(self) -> bool:
        return self.current >= self.target

    @property
    def progress_pct(self) -> int:
        return min(100, round(self.current / self.target * 100)) if self.target else 0


def _achievements(stats: dict) -> list:
    s = stats
    return [
        Achievement(
            "first_quiz",
            "Primus gradus",
            "Rond je eerste quiz af",
            "flag-checkered",
            s["quizzes"],
            1,
        ),
        Achievement(
            "quizzes_10",
            "Assiduus",
            "Rond 10 quizzen af",
            "list-check",
            s["quizzes"],
            10,
        ),
        Achievement(
            "quizzes_50",
            "Indefessus",
            "Rond 50 quizzen af",
            "dumbbell",
            s["quizzes"],
            50,
        ),
        Achievement(
            "perfect",
            "Sine errore",
            f"Een foutloze quiz van minstens {PERFECT_MIN_QUESTIONS} vragen",
            "star",
            s["perfect"],
            1,
        ),
        Achievement(
            "perfect_5", "Perfectio", "5 foutloze quizzen", "crown", s["perfect"], 5
        ),
        Achievement(
            "mixed", "Miscellanea", "Speel een gemengde quiz", "shuffle", s["mixed"], 1
        ),
        Achievement(
            "correct_100",
            "Centurio",
            "100 goede antwoorden",
            "shield-halved",
            s["correct"],
            100,
        ),
        Achievement(
            "correct_1000",
            "Legio",
            "1000 goede antwoorden",
            "chess-rook",
            s["correct"],
            1000,
        ),
        Achievement(
            "streak_3",
            "Tres dies",
            "3 dagen op rij geoefend",
            "fire",
            s["longest_streak"],
            3,
        ),
        Achievement(
            "streak_7",
            "Hebdomas",
            "7 dagen op rij geoefend",
            "fire-flame-curved",
            s["longest_streak"],
            7,
        ),
        Achievement(
            "streak_30",
            "Mensis",
            "30 dagen op rij geoefend",
            "calendar-check",
            s["longest_streak"],
            30,
        ),
        Achievement(
            "mastered_25", "Memoria", "25 woorden beheerst", "brain", s["mastered"], 25
        ),
        Achievement(
            "mastered_100",
            "Thesaurus",
            "100 woorden beheerst",
            "gem",
            s["mastered"],
            100,
        ),
        Achievement(
            "level_5", "Grammaticus", "Bereik level 5", "graduation-cap", s["level"], 5
        ),
        Achievement(
            "level_10", "Magistra", "Bereik level 10", "landmark", s["level"], 10
        ),
    ]


# --- Profile ---------------------------------------------------------------


@dataclass
class Profile:
    xp: int
    level: int
    title: str
    next_title: str
    xp_into_level: int
    xp_for_level: int
    streak: int
    longest_streak: int
    practiced_today: bool
    today_correct: int
    daily_goal: int
    correct: int
    quizzes: int
    mastered: int
    achievements: list = field(default_factory=list)

    @property
    def level_pct(self) -> int:
        return min(100, round(self.xp_into_level / self.xp_for_level * 100))

    @property
    def daily_pct(self) -> int:
        return min(100, round(self.today_correct / self.daily_goal * 100))

    @property
    def daily_done(self) -> bool:
        return self.today_correct >= self.daily_goal

    @property
    def unlocked(self) -> list:
        return [a for a in self.achievements if a.unlocked]

    @property
    def next_achievement(self) -> Optional[Achievement]:
        """The locked achievement that is closest to being unlocked."""
        locked = [a for a in self.achievements if not a.unlocked]
        return max(locked, key=lambda a: a.current / a.target, default=None)


def _streaks(days: set, today: date) -> tuple:
    """Return (current streak, longest streak) from a set of practice dates.

    The current streak is still alive if you practised yesterday but not yet today.
    """
    if not days:
        return 0, 0
    current = 0
    cursor = today if today in days else today - timedelta(days=1)
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)

    longest = run = 0
    previous = None
    for day in sorted(days):
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    return current, longest


def build_profile(exclude_session_id: Optional[int] = None) -> Profile:
    """Compute the player's profile. Pass exclude_session_id to see the state
    from before that quiz (used to detect level-ups and new achievements)."""
    answers = db.session.query(
        QuizAnswer.is_correct, QuizAnswer.answered_at, QuizAnswer.session_id
    )
    sessions = QuizSession.query.filter_by(status="completed")
    if exclude_session_id is not None:
        answers = answers.filter(QuizAnswer.session_id != exclude_session_id)
        sessions = sessions.filter(QuizSession.id != exclude_session_id)
    answers = answers.all()
    sessions = sessions.all()

    correct = sum(1 for is_correct, _, _ in answers if is_correct)
    wrong = len(answers) - correct
    # Wrong answers are asked again until correct, so correct_answers can still
    # reach total_questions. A perfect quiz is one without any wrong answer.
    sessions_with_mistakes = {sid for is_correct, _, sid in answers if not is_correct}
    perfect = sum(
        1
        for s in sessions
        if s.total_questions >= PERFECT_MIN_QUESTIONS
        and s.id not in sessions_with_mistakes
    )
    mixed = sum(1 for s in sessions if s.quiz_type == "mixed")

    xp = (
        correct * XP_CORRECT
        + wrong * XP_WRONG
        + len(sessions) * XP_QUIZ_COMPLETED
        + perfect * XP_PERFECT_QUIZ
    )
    level = level_for_xp(xp)

    today = utcnow().date()
    days = {answered_at.date() for _, answered_at, _ in answers if answered_at}
    streak, longest = _streaks(days, today)
    today_correct = sum(
        1
        for is_correct, answered_at, _ in answers
        if is_correct and answered_at and answered_at.date() == today
    )

    mastered = (
        Entry.query.filter(
            Entry.correct_count >= 5,
            Entry.correct_count
            >= 0.85 * (Entry.correct_count + func.coalesce(Entry.incorrect_count, 0)),
        ).count()
        if exclude_session_id is None
        else _mastered_before(exclude_session_id)
    )

    stats = dict(
        quizzes=len(sessions),
        perfect=perfect,
        mixed=mixed,
        correct=correct,
        longest_streak=longest,
        mastered=mastered,
        level=level,
    )
    return Profile(
        xp=xp,
        level=level,
        title=level_title(level),
        next_title=level_title(level + 1),
        xp_into_level=xp - level_floor(level),
        xp_for_level=level_floor(level + 1) - level_floor(level),
        streak=streak,
        longest_streak=longest,
        practiced_today=today in days,
        today_correct=today_correct,
        daily_goal=DAILY_GOAL,
        correct=correct,
        quizzes=len(sessions),
        mastered=mastered,
        achievements=_achievements(stats),
    )


def _mastered_before(session_id: int) -> int:
    """Mastered-word count with this session's answers taken back out."""
    rows = (
        db.session.query(
            QuizAnswer.entry_id,
            func.sum(db.case((QuizAnswer.is_correct, 1), else_=0)),
            func.sum(db.case((QuizAnswer.is_correct, 0), else_=1)),
        )
        .filter(QuizAnswer.session_id == session_id)
        .group_by(QuizAnswer.entry_id)
        .all()
    )
    delta = {entry_id: (c, w) for entry_id, c, w in rows}
    count = 0
    for entry in Entry.query.filter(Entry.correct_count >= 5).all():
        c, w = delta.get(entry.id, (0, 0))
        before = _Counts(entry.correct_count - c, (entry.incorrect_count or 0) - w)
        if mastery(before) == 3:
            count += 1
    return count


@dataclass
class _Counts:
    correct_count: int
    incorrect_count: int


# --- Quiz helpers ----------------------------------------------------------


def current_combo(session_id: Optional[int]) -> int:
    """Number of consecutive correct answers at the end of a quiz session."""
    if not session_id:
        return 0
    results = (
        db.session.query(QuizAnswer.is_correct)
        .filter_by(session_id=session_id)
        .order_by(QuizAnswer.id.desc())
        .limit(200)
        .all()
    )
    combo = 0
    for (is_correct,) in results:
        if not is_correct:
            break
        combo += 1
    return combo


def quiz_rewards(session_id: Optional[int]) -> Optional[dict]:
    """What a just-completed quiz earned: XP, level-up and new achievements."""
    if not session_id:
        return None
    before = build_profile(exclude_session_id=session_id)
    after = build_profile()
    unlocked_before = {a.key for a in before.unlocked}
    mistakes = QuizAnswer.query.filter_by(
        session_id=session_id, is_correct=False
    ).count()
    return {
        "mistakes": mistakes,
        "xp_gained": after.xp - before.xp,
        "level_before": before.level,
        "leveled_up": after.level > before.level,
        "new_achievements": [a for a in after.unlocked if a.key not in unlocked_before],
        "streak_extended": after.streak > before.streak,
        "profile": after,
    }
