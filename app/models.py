from datetime import datetime
from app import db

class WordList(db.Model):
    __tablename__ = 'word_lists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_language = db.Column(db.String(50), nullable=False)
    target_language = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship('Word', backref='word_list', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<WordList {self.name}>'

class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('word_lists.id'), nullable=False)
    source_word = db.Column(db.String(200), nullable=False)
    target_word = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Word {self.source_word} -> {self.target_word}>'
