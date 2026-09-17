# flask_app/app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class TaskStatus(enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    boards = db.relationship("Board", back_populates="owner")

class Board(db.Model):
    __tablename__ = "boards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="boards")
    tasks = db.relationship("Task", back_populates="board", cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", back_populates="board", cascade="all, delete-orphan")

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.todo, nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    board = db.relationship("Board", back_populates="tasks")

class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    board = db.relationship("Board", back_populates="attachments")