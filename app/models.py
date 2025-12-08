from datetime import datetime

from app import db


class Language(db.Model):
    """Vaste talenlijst voor filtering"""

    __tablename__ = "languages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True)

    def __repr__(self):
        return f"<Language {self.name}>"


class Category(db.Model):
    """Categorieën voor lijsten"""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    lists = db.relationship("List", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class List(db.Model):
    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_language_id = db.Column(
        db.Integer, db.ForeignKey("languages.id"), nullable=False
    )
    target_language_id = db.Column(
        db.Integer, db.ForeignKey("languages.id"), nullable=False
    )
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Je krijgt alsnog twee relaties -> alleen nu aan de goede kant gedefinieerd
    source_language = db.relationship(
        "Language",
        foreign_keys=[source_language_id],
        backref="source_lists",
    )

    target_language = db.relationship(
        "Language",
        foreign_keys=[target_language_id],
        backref="target_lists",
    )

    entries = db.relationship(
        "Entry", backref="list", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<List {self.name}>"


class Entry(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    source_word = db.Column(db.String(200), nullable=False)
    target_word = db.Column(db.String(200), nullable=False)
    entry_type = db.Column(db.String(20), default="word", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Entry {self.source_word} -> {self.target_word}>"

    @property
    def success_rate(self):
        """Calculate success rate as a percentage (0-100)"""
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return None
        return round((self.correct_count / total) * 100, 1)

    @property
    def total_attempts(self):
        """Total number of quiz attempts for this entry"""
        return self.correct_count + self.incorrect_count


class QuizSession(db.Model):
    __tablename__ = "quiz_sessions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_type = db.Column(db.String(20), nullable=False)  # 'single' or 'mixed'
    direction = db.Column(
        db.String(20), nullable=False
    )  # 'forward', 'reverse', 'random'
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    current_index = db.Column(
        db.Integer, nullable=False, default=0
    )  # Current question position
    status = db.Column(
        db.String(20), nullable=False, default="in_progress"
    )  # 'in_progress', 'completed', 'abandoned'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    quiz_data = db.Column(db.JSON, nullable=True)  # Store quiz questions and state

    # Relationships
    answers = db.relationship(
        "QuizAnswer", backref="session", lazy=True, cascade="all, delete-orphan"
    )
    session_lists = db.relationship(
        "QuizSessionList", backref="session", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<QuizSession {self.id} - {self.correct_answers}/{self.total_questions}>"
        )

    @property
    def score_percentage(self):
        """Calculate score as percentage"""
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 1)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "quiz_type": self.quiz_type,
            "direction": self.direction,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score_percentage": self.score_percentage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


class QuizAnswer(db.Model):
    __tablename__ = "quiz_answers"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("quiz_sessions.id"), nullable=False
    )
    entry_id = db.Column(db.Integer, db.ForeignKey("entries.id"), nullable=False)
    user_answer = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    question_direction = db.Column(
        db.String(20), nullable=False
    )  # 'forward' or 'reverse'
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to entry
    entry = db.relationship("Entry", backref="quiz_answers")

    def __repr__(self):
        return f"<QuizAnswer {self.user_answer} -> {self.correct_answer} ({'✓' if self.is_correct else '✗'})>"


class QuizSessionList(db.Model):
    __tablename__ = "quiz_session_lists"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("quiz_sessions.id"), nullable=False
    )
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)

    # Relationship to list
    list = db.relationship("List", backref="quiz_sessions")

    def __repr__(self):
        return f"<QuizSessionList session={self.session_id} list={self.list_id}>"
