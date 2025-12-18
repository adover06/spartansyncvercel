"""
Pytest configuration and fixtures for the LMS application.
"""

import pytest
import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Course, Assignment, Announcement, Submission, RubricCriterion


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app = create_app("tests.config.TestConfig")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide a test client for making requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provide a CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def app_context(app):
    """Provide application context for database operations."""
    with app.app_context():
        yield app


@pytest.fixture
def student_user(app_context):
    """Create a test student user."""
    user = User(
        username="teststudent",
        email="student@test.com",
        role="student"
    )
    user.password = generate_password_hash("password123", method='pbkdf2:sha256')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def instructor_user(app_context):
    """Create a test instructor user."""
    user = User(
        username="testinstructor",
        email="instructor@test.com",
        role="instructor"
    )
    user.password = generate_password_hash("password123", method='pbkdf2:sha256')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ta_user(app_context):
    """Create a test teaching assistant user."""
    user = User(
        username="testta",
        email="ta@test.com",
        role="ta"
    )
    user.password = generate_password_hash("password123", method='pbkdf2:sha256')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def course(app_context):
    """Create a test course."""
    course = Course(
        course_name="Introduction to Python",
        course_code="CS101",
        description="Learn the basics of Python programming"
    )
    db.session.add(course)
    db.session.commit()
    return course


@pytest.fixture
def multiple_courses(app_context):
    """Create multiple test courses."""
    courses = [
        Course(course_name="Python Basics", course_code="CS101", description="Intro to Python"),
        Course(course_name="Web Development", course_code="CS201", description="Web dev with Flask"),
        Course(course_name="Database Design", course_code="CS301", description="SQL and databases"),
    ]
    db.session.add_all(courses)
    db.session.commit()
    return courses


@pytest.fixture
def assignment(app_context, course, instructor_user):
    """Create a test assignment."""
    from datetime import datetime, timedelta
    
    due_date = datetime.utcnow() + timedelta(days=7)
    assignment = Assignment(
        title="Python Assignment 1",
        description="Write a function to calculate factorial",
        due_date=due_date,
        points=100,
        status="Published",
        allow_submissions=True,
        course_id=course.id,
        created_by=instructor_user.id
    )
    db.session.add(assignment)
    db.session.commit()
    return assignment


@pytest.fixture
def multiple_assignments(app_context, course, instructor_user):
    """Create multiple test assignments."""
    from datetime import datetime, timedelta
    
    assignments = []
    for i in range(3):
        due_date = datetime.utcnow() + timedelta(days=7+i)
        assignment = Assignment(
            title=f"Assignment {i+1}",
            description=f"Description for assignment {i+1}",
            due_date=due_date,
            points=100,
            status="Published",
            allow_submissions=True,
            course_id=course.id,
            created_by=instructor_user.id
        )
        assignments.append(assignment)
    
    db.session.add_all(assignments)
    db.session.commit()
    return assignments


@pytest.fixture
def submission(app_context, assignment, student_user):
    """Create a test submission."""
    from datetime import datetime
    
    submission = Submission(
        assignment_id=assignment.id,
        student_id=student_user.id,
        content="This is my assignment submission",
        status="Submitted",
        submitted_at=datetime.utcnow()
    )
    db.session.add(submission)
    db.session.commit()
    return submission


@pytest.fixture
def announcement(app_context, course, instructor_user):
    """Create a test announcement."""
    from datetime import datetime
    
    announcement = Announcement(
        title="Welcome to the course!",
        body="This is the course announcement. Welcome everyone!",
        course_id=course.id,
        created_by=instructor_user.id,
        created_at=datetime.utcnow()
    )
    db.session.add(announcement)
    db.session.commit()
    return announcement


@pytest.fixture
def rubric_criterion(app_context, assignment):
    """Create a test rubric criterion."""
    criterion = RubricCriterion(
        assignment_id=assignment.id,
        title="Code Quality",
        description="Evaluate the quality of the submitted code",
        max_points=50
    )
    db.session.add(criterion)
    db.session.commit()
    return criterion
