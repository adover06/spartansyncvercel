import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "s12hyp981"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # weights for assignment categories (must sum to 100)
    GRADE_WEIGHTS = {
        "homework": 30,
        "exam": 50,
        "project": 20,
    }

    # choices for assignment creation forms
    ASSIGNMENT_CATEGORIES = [
        ("homework", "Homework"),
        ("exam", "Exam"),
        ("project", "Project"),
    ]
