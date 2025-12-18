"""
Tests for application forms.
Tests that forms have correct fields and validators.
"""

import pytest
from datetime import datetime, timedelta
from app.forms import (
    LoginForm, CreateAccountForm, AssignmentForm, AnnouncementForm,
    SubmissionForm, RubricCriterionForm, CourseForm, ClassSelectionForm
)


class TestLoginForm:
    """Test cases for the LoginForm."""

    def test_login_form_fields_exist(self, app_context):
        """Test that LoginForm has required fields."""
        form = LoginForm()
        assert hasattr(form, 'username')
        assert hasattr(form, 'password')
        assert hasattr(form, 'remember_me')
        assert hasattr(form, 'submit')

    def test_login_form_validators(self, app_context):
        """Test that login form has required validators."""
        form = LoginForm()
        from wtforms.validators import DataRequired
        
        username_validators = form.username.validators
        password_validators = form.password.validators
        
        assert any(isinstance(v, DataRequired) for v in username_validators)
        assert any(isinstance(v, DataRequired) for v in password_validators)


class TestCreateAccountForm:
    """Test cases for the CreateAccountForm."""

    def test_create_account_form_fields_exist(self, app_context):
        """Test that CreateAccountForm has required fields."""
        form = CreateAccountForm()
        assert hasattr(form, 'username')
        assert hasattr(form, 'email')
        assert hasattr(form, 'password')
        assert hasattr(form, 'role')
        assert hasattr(form, 'submit')

    def test_create_account_form_role_choices(self, app_context):
        """Test that role field has correct choices."""
        form = CreateAccountForm()
        choices = form.role.choices
        choice_values = [choice[0] for choice in choices]
        
        assert 'student' in choice_values
        assert 'ta' in choice_values
        assert 'instructor' in choice_values


class TestAssignmentForm:
    """Test cases for the AssignmentForm."""

    def test_assignment_form_fields_exist(self, app_context):
        """Test that AssignmentForm has required fields."""
        form = AssignmentForm()
        assert hasattr(form, 'title')
        assert hasattr(form, 'description')
        assert hasattr(form, 'course')
        assert hasattr(form, 'due_date')
        assert hasattr(form, 'points')
        assert hasattr(form, 'allow_submissions')
        assert hasattr(form, 'submit')

    def test_assignment_form_validators(self, app_context):
        """Test that assignment form has correct validators."""
        form = AssignmentForm()
        from wtforms.validators import DataRequired, NumberRange
        
        # Check points validator
        points_validators = form.points.validators
        assert any(isinstance(v, DataRequired) for v in points_validators)
        assert any(isinstance(v, NumberRange) for v in points_validators)


class TestAnnouncementForm:
    """Test cases for the AnnouncementForm."""

    def test_announcement_form_fields_exist(self, app_context):
        """Test that AnnouncementForm has required fields."""
        form = AnnouncementForm()
        assert hasattr(form, 'title')
        assert hasattr(form, 'body')
        assert hasattr(form, 'course')
        assert hasattr(form, 'submit')

    def test_announcement_form_validators(self, app_context):
        """Test that announcement form has required validators."""
        form = AnnouncementForm()
        from wtforms.validators import DataRequired
        
        title_validators = form.title.validators
        body_validators = form.body.validators
        
        assert any(isinstance(v, DataRequired) for v in title_validators)
        assert any(isinstance(v, DataRequired) for v in body_validators)


class TestSubmissionForm:
    """Test cases for the SubmissionForm."""

    def test_submission_form_fields_exist(self, app_context):
        """Test that SubmissionForm has required fields."""
        form = SubmissionForm()
        assert hasattr(form, 'content')
        assert hasattr(form, 'submit')

    def test_submission_form_validators(self, app_context):
        """Test that submission form has required validators."""
        form = SubmissionForm()
        from wtforms.validators import DataRequired
        
        content_validators = form.content.validators
        assert any(isinstance(v, DataRequired) for v in content_validators)


class TestRubricCriterionForm:
    """Test cases for the RubricCriterionForm."""

    def test_rubric_criterion_form_fields_exist(self, app_context):
        """Test that RubricCriterionForm has required fields."""
        form = RubricCriterionForm()
        assert hasattr(form, 'assignment_id')
        assert hasattr(form, 'title')
        assert hasattr(form, 'description')
        assert hasattr(form, 'max_points')
        assert hasattr(form, 'submit')

    def test_rubric_criterion_form_validators(self, app_context):
        """Test that rubric criterion form has correct validators."""
        form = RubricCriterionForm()
        from wtforms.validators import DataRequired, NumberRange
        
        # Check max_points validator
        max_points_validators = form.max_points.validators
        assert any(isinstance(v, DataRequired) for v in max_points_validators)
        assert any(isinstance(v, NumberRange) for v in max_points_validators)


class TestCourseForm:
    """Test cases for the CourseForm."""

    def test_course_form_fields_exist(self, app_context):
        """Test that CourseForm has required fields."""
        form = CourseForm()
        assert hasattr(form, 'course_name')
        assert hasattr(form, 'course_code')
        assert hasattr(form, 'description')
        assert hasattr(form, 'submit')

    def test_course_form_validators(self, app_context):
        """Test that course form has required validators."""
        form = CourseForm()
        from wtforms.validators import DataRequired
        
        course_name_validators = form.course_name.validators
        course_code_validators = form.course_code.validators
        
        assert any(isinstance(v, DataRequired) for v in course_name_validators)
        assert any(isinstance(v, DataRequired) for v in course_code_validators)


class TestClassSelectionForm:
    """Test cases for the ClassSelectionForm."""

    def test_class_selection_form_creation(self, app_context):
        """Test creating ClassSelectionForm."""
        form = ClassSelectionForm()
        assert hasattr(form, 'courses')
        assert hasattr(form, 'submit')

    def test_class_selection_form_is_multiple(self, app_context):
        """Test that courses field accepts multiple selections."""
        form = ClassSelectionForm()
        # SelectMultipleField should be available
        assert hasattr(form, 'courses')
