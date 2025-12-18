from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False, default="student")  # student, instructor, ta

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<user {self.id}: {self.username}>'

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.ForeignKey('user.id'), nullable=False)
    classes = db.Column(db.JSON, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100)
    category = db.Column(db.String(20), nullable=False, default="homework")  # added homework, exam, project
    status = db.Column(db.String(20), nullable=False, default="Published")
    allow_submissions = db.Column(db.Boolean, nullable=False, default=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    course = db.relationship("Course")
    creator = db.relationship("User", foreign_keys=[created_by])


class RubricCriterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_points = db.Column(db.Integer, nullable=False)

    assignment = db.relationship("Assignment", backref="rubric_criteria", lazy=True)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Submitted")
    score = db.Column(db.Integer, nullable=True)
    rubric_scores = db.Column(db.JSON, nullable=True)

    assignment = db.relationship("Assignment", backref="submissions", lazy=True)
    student = db.relationship("User", foreign_keys=[student_id])


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    course = db.relationship("Course")
    author = db.relationship("User", foreign_keys=[created_by])


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    is_group = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participants = db.relationship(
        "ConversationParticipant",
        backref="conversation",
        cascade="all, delete-orphan",
        lazy=True,
    )

    messages = db.relationship(
        "Message",
        backref="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy=True,
    )

    def last_message(self):
        if not self.messages:
            return None
        return self.messages[-1]

    def unread_count_for(self, user_id):
        part = ConversationParticipant.query.filter_by(conversation_id=self.id, user_id=user_id).first()
        if not part:
            return 0
        last_read = part.last_read_at
        if not last_read:
            # all messages are unread
            return len(self.messages)
        return sum(1 for m in self.messages if m.created_at > last_read)


class ConversationParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    last_read_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversation.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
