"""
Tests for application models.
Tests User, Course, Assignment, Submission, Announcement, and RubricCriterion models.
"""

import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import (
    User, Course, Assignment, Submission, Announcement, RubricCriterion, Classes
)


class TestUserModel:
    """Test cases for the User model."""

    def test_user_creation(self, app_context):
        """Test creating a new user."""
        user = User(
            username="john_doe",
            email="john@example.com",
            role="student"
        )
        user.password = generate_password_hash("securepassword", method='pbkdf2:sha256')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.role == "student"

    def test_password_hashing(self, app_context):
        """Test that passwords are properly hashed."""
        user = User(username="testuser", email="test@example.com")
        password = "mypassword123"
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        assert user.password != password
        
    def test_check_password_correct(self, app_context):
        """Test checking a correct password."""
        user = User(username="testuser", email="test@example.com")
        password = "correctpassword"
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        
        assert user.check_password(password) is True

    def test_check_password_incorrect(self, app_context):
        """Test checking an incorrect password."""
        user = User(username="testuser", email="test@example.com")
        user.password = generate_password_hash("correctpassword", method='pbkdf2:sha256')
        
        assert user.check_password("wrongpassword") is False

    def test_user_repr(self, student_user):
        """Test the User __repr__ method."""
        repr_str = repr(student_user)
        assert "user" in repr_str.lower()
        assert "teststudent" in repr_str

    def test_user_uniqueness_username(self, app_context, student_user):
        """Test that usernames must be unique."""
        with pytest.raises(Exception):
            duplicate = User(
                username="teststudent",  # Same as student_user
                email="another@example.com",
                password="somehash"
            )
            db.session.add(duplicate)
            db.session.commit()

    def test_user_uniqueness_email(self, app_context, student_user):
        """Test that emails must be unique."""
        with pytest.raises(Exception):
            duplicate = User(
                username="newuser",
                email="student@test.com",  # Same as student_user
                password="somehash"
            )
            db.session.add(duplicate)
            db.session.commit()

    def test_user_roles(self, app_context):
        """Test different user roles."""
        roles = ["student", "ta", "instructor"]
        for role in roles:
            user = User(
                username=f"user_{role}",
                email=f"{role}@example.com",
                role=role,
                password=generate_password_hash("pass", method='pbkdf2:sha256')
            )
            db.session.add(user)
        db.session.commit()
        
        assert User.query.filter_by(role="student").first() is not None
        assert User.query.filter_by(role="ta").first() is not None
        assert User.query.filter_by(role="instructor").first() is not None


class TestCourseModel:
    """Test cases for the Course model."""

    def test_course_creation(self, app_context):
        """Test creating a new course."""
        course = Course(
            course_name="Advanced Python",
            course_code="CS301",
            description="Advanced concepts in Python"
        )
        db.session.add(course)
        db.session.commit()
        
        assert course.id is not None
        assert course.course_name == "Advanced Python"
        assert course.course_code == "CS301"

    def test_course_unique_code(self, app_context, course):
        """Test that course codes must be unique."""
        with pytest.raises(Exception):
            duplicate_course = Course(
                course_name="Different Name",
                course_code="CS101",  # Same as course fixture
                description="Test"
            )
            db.session.add(duplicate_course)
            db.session.commit()

    def test_course_optional_description(self, app_context):
        """Test creating a course without a description."""
        course = Course(
            course_name="Web Dev",
            course_code="CS201"
        )
        db.session.add(course)
        db.session.commit()
        
        assert course.description is None

    def test_multiple_courses(self, app_context, multiple_courses):
        """Test querying multiple courses."""
        courses = Course.query.all()
        assert len(courses) == 3
        
        course_names = [c.course_name for c in courses]
        assert "Python Basics" in course_names
        assert "Web Development" in course_names
        assert "Database Design" in course_names


class TestAssignmentModel:
    """Test cases for the Assignment model."""

    def test_assignment_creation(self, app_context, course, instructor_user):
        """Test creating a new assignment."""
        due_date = datetime.utcnow() + timedelta(days=7)
        assignment = Assignment(
            title="Midterm Exam",
            description="Comprehensive exam covering weeks 1-8",
            due_date=due_date,
            points=150,
            course_id=course.id,
            created_by=instructor_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.id is not None
        assert assignment.title == "Midterm Exam"
        assert assignment.points == 150
        assert assignment.allow_submissions is True  # Default value

    def test_assignment_default_status(self, assignment):
        """Test that assignments default to 'Published' status."""
        assert assignment.status == "Published"

    def test_assignment_allow_submissions_default(self, assignment):
        """Test that allow_submissions defaults to True."""
        assert assignment.allow_submissions is True

    def test_assignment_relationships(self, app_context, course, instructor_user):
        """Test assignment relationships with course and user."""
        due_date = datetime.utcnow() + timedelta(days=7)
        assignment = Assignment(
            title="Test Assignment",
            description="Test",
            due_date=due_date,
            points=100,
            course_id=course.id,
            created_by=instructor_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.course.course_name == "Introduction to Python"
        assert assignment.creator.username == "testinstructor"

    def test_assignment_overdue_status(self, app_context, course, instructor_user):
        """Test creating an overdue assignment."""
        past_date = datetime.utcnow() - timedelta(days=1)
        assignment = Assignment(
            title="Past Assignment",
            description="This was due yesterday",
            due_date=past_date,
            points=100,
            course_id=course.id,
            created_by=instructor_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.due_date < datetime.utcnow()

    def test_assignment_closed_submissions(self, app_context, course, instructor_user):
        """Test closing submissions for an assignment."""
        due_date = datetime.utcnow() + timedelta(days=7)
        assignment = Assignment(
            title="Test Assignment",
            description="Test",
            due_date=due_date,
            allow_submissions=False,
            points=100,
            course_id=course.id,
            created_by=instructor_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.allow_submissions is False

    def test_multiple_assignments_order(self, app_context, multiple_assignments):
        """Test querying and ordering multiple assignments."""
        assignments = Assignment.query.order_by(Assignment.due_date).all()
        assert len(assignments) == 3
        
        # Verify they're ordered by due date
        for i in range(len(assignments) - 1):
            assert assignments[i].due_date <= assignments[i+1].due_date


class TestSubmissionModel:
    """Test cases for the Submission model."""

    def test_submission_creation(self, app_context, assignment, student_user):
        """Test creating a new submission."""
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student_user.id,
            content="My submission content",
            status="Submitted"
        )
        db.session.add(submission)
        db.session.commit()
        
        assert submission.id is not None
        assert submission.status == "Submitted"
        assert submission.content == "My submission content"

    def test_submission_default_status(self, submission):
        """Test that submissions default to 'Submitted' status."""
        assert submission.status == "Submitted"

    def test_submission_timestamp(self, submission):
        """Test that submission has a timestamp."""
        assert submission.submitted_at is not None
        assert isinstance(submission.submitted_at, datetime)

    def test_submission_grading(self, app_context, submission):
        """Test updating submission with grade."""
        submission.status = "Graded"
        submission.score = 95
        submission.rubric_scores = {"criterion1": 50, "criterion2": 45}
        db.session.commit()
        
        assert submission.status == "Graded"
        assert submission.score == 95
        assert submission.rubric_scores["criterion1"] == 50

    def test_submission_relationships(self, submission, assignment, student_user):
        """Test submission relationships with assignment and student."""
        assert submission.assignment.title == assignment.title
        assert submission.student.username == student_user.username


class TestAnnouncementModel:
    """Test cases for the Announcement model."""

    def test_announcement_creation(self, app_context, course, instructor_user):
        """Test creating a new announcement."""
        announcement = Announcement(
            title="Important Update",
            body="Please read the following important information...",
            course_id=course.id,
            created_by=instructor_user.id
        )
        db.session.add(announcement)
        db.session.commit()
        
        assert announcement.id is not None
        assert announcement.title == "Important Update"

    def test_announcement_timestamp(self, announcement):
        """Test that announcement has a creation timestamp."""
        assert announcement.created_at is not None
        assert isinstance(announcement.created_at, datetime)

    def test_announcement_relationships(self, announcement, course, instructor_user):
        """Test announcement relationships with course and author."""
        assert announcement.course.course_name == course.course_name
        assert announcement.author.username == instructor_user.username

    def test_announcement_without_course(self, app_context, instructor_user):
        """Test creating an announcement without a specific course (general announcement)."""
        announcement = Announcement(
            title="General Announcement",
            body="This applies to everyone",
            course_id=None,
            created_by=instructor_user.id
        )
        db.session.add(announcement)
        db.session.commit()
        
        assert announcement.course_id is None


class TestRubricCriterionModel:
    """Test cases for the RubricCriterion model."""

    def test_rubric_criterion_creation(self, app_context, assignment):
        """Test creating a rubric criterion."""
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title="Code Efficiency",
            description="Evaluate code efficiency and performance",
            max_points=25
        )
        db.session.add(criterion)
        db.session.commit()
        
        assert criterion.id is not None
        assert criterion.title == "Code Efficiency"
        assert criterion.max_points == 25

    def test_rubric_criterion_optional_description(self, app_context, assignment):
        """Test creating a rubric criterion without description."""
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title="Functionality",
            max_points=50
        )
        db.session.add(criterion)
        db.session.commit()
        
        assert criterion.description is None

    def test_rubric_criterion_relationship(self, rubric_criterion, assignment):
        """Test rubric criterion relationship with assignment."""
        assert rubric_criterion.assignment.id == assignment.id

    def test_multiple_rubric_criteria(self, app_context, assignment):
        """Test creating multiple criteria for one assignment."""
        criteria = [
            RubricCriterion(
                assignment_id=assignment.id,
                title="Criterion 1",
                max_points=30
            ),
            RubricCriterion(
                assignment_id=assignment.id,
                title="Criterion 2",
                max_points=40
            ),
            RubricCriterion(
                assignment_id=assignment.id,
                title="Criterion 3",
                max_points=30
            ),
        ]
        db.session.add_all(criteria)
        db.session.commit()
        
        assignment_criteria = RubricCriterion.query.filter_by(
            assignment_id=assignment.id
        ).all()
        assert len(assignment_criteria) == 3
        
        total_points = sum(c.max_points for c in assignment_criteria)
        assert total_points == 100


class TestClassesModel:
    """Test cases for the Classes model."""

    def test_classes_creation(self, app_context, student_user):
        """Test creating a classes record."""
        classes_data = [1, 2, 3]  # Course IDs
        classes = Classes(
            user=student_user.id,
            classes=classes_data
        )
        db.session.add(classes)
        db.session.commit()
        
        assert classes.id is not None
        assert classes.user == student_user.id
        assert classes.classes == classes_data

    def test_classes_json_storage(self, app_context, student_user):
        """Test storing complex JSON in classes field."""
        classes_data = [
            {"id": 1, "course_code": "CS101"},
            {"id": 2, "course_code": "CS201"},
        ]
        classes = Classes(
            user=student_user.id,
            classes=classes_data
        )
        db.session.add(classes)
        db.session.commit()
        
        retrieved = Classes.query.filter_by(user=student_user.id).first()
        assert len(retrieved.classes) == 2
        assert retrieved.classes[0]["course_code"] == "CS101"
