"""
Tests for application routes (Auth and Main).
Tests authentication, course management, assignment management, and submissions.
"""

import pytest
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Course, Assignment, Submission, Announcement


class TestAuthRoutes:
    """Test cases for authentication routes."""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200

    def test_create_account_page_loads(self, client):
        """Test that account creation page loads."""
        response = client.get('/createaccount')
        assert response.status_code == 200

    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123',
            'remember_me': False
        })
        assert response.status_code == 200

    def test_create_account_successful(self, client):
        """Test successful account creation."""
        response = client.post('/createaccount', data={
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'password': 'newpass123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Verify user was created
        user = User.query.filter_by(username='newstudent').first()
        assert user is not None
        assert user.role == 'student'

    def test_create_account_duplicate_username(self, client, student_user):
        """Test account creation with duplicate username."""
        response = client.post('/createaccount', data={
            'username': 'teststudent',  # Already exists
            'email': 'different@example.com',
            'password': 'newpass123',
            'role': 'student'
        })
        
        assert response.status_code == 200
        assert b'already exists' in response.data

    def test_logout_requires_login(self, client):
        """Test that logout requires being logged in."""
        response = client.get('/logout')
        assert response.status_code in [302, 401]


class TestMainRoutes:
    """Test cases for main application routes."""

    def test_home_redirect_unauthenticated(self, client):
        """Test that home page redirects unauthenticated users."""
        response = client.get('/home')
        assert response.status_code == 302  # Redirect

    def test_home_loads_authenticated(self, client, student_user):
        """Test home page loads for authenticated users."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/home')
            assert response.status_code == 200

    def test_courses_page(self, client, student_user):
        """Test courses page."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/courses')
            assert response.status_code == 200

    def test_assignments_list_page(self, client, student_user):
        """Test assignments list page."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/assignments')
            assert response.status_code == 200

    def test_course_create_requires_instructor(self, client, student_user):
        """Test that course creation requires instructor role."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/courses/new', follow_redirects=True)
            assert response.status_code == 200

    def test_course_create_instructor(self, client, instructor_user):
        """Test course creation by instructor."""
        with client:
            client.post('/login', data={
                'username': 'testinstructor',
                'password': 'password123'
            })
            response = client.post('/courses/new', data={
                'course_name': 'New Course',
                'course_code': 'CS999',
                'description': 'A new test course'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            # Verify course was created
            new_course = Course.query.filter_by(course_code='CS999').first()
            assert new_course is not None

    def test_course_detail_page(self, client, student_user, course):
        """Test course detail page."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get(f'/courses/{course.id}')
            assert response.status_code == 200

    def test_course_detail_nonexistent(self, client, student_user):
        """Test course detail page with nonexistent course."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/courses/99999')
            assert response.status_code == 404

    def test_manage_classes_page(self, client, student_user):
        """Test manage classes page."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/classes/manage')
            assert response.status_code in [200, 302]
    
    def test_study_plan_page_for_student(self, client, student_user):
        """Test study plan page for students only"""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/study-plan')
            assert response.status_code in [200]
        
    def test_study_plan_page_for_instructor_denied(self, client, instructor_user):
        """Test study plan page inaccessible to instructors"""
        with client:
            client.post('/login', data={
                'username': 'testinstructor',
                'password': 'password123'
            })
            response = client.get('/study-plan', follow_redirects=True)
            assert response.status_code == 200
            assert b"You do not have permission" in response.data

    def test_assignment_create_requires_instructor(self, client, student_user):
        """Test that assignment creation requires instructor role."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.get('/assignments/new', follow_redirects=True)
            assert response.status_code == 200

    def test_assignment_create_instructor(self, client, instructor_user, course):
        """Test assignment creation by instructor."""
        with client:
            client.post('/login', data={
                'username': 'testinstructor',
                'password': 'password123'
            })
            
            due_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")
            
            response = client.post('/assignments/new', data={
                'title': 'New Assignment',
                'description': 'Assignment description',
                'course': course.id,
                'due_date': due_date,
                'points': 100,
                'allow_submissions': True
            }, follow_redirects=True)
            
            assert response.status_code == 200


class TestRoutePermissions:
    """Test permission checking in routes."""

    def test_student_cannot_create_courses(self, client, student_user):
        """Test that students cannot create courses."""
        with client:
            client.post('/login', data={
                'username': 'teststudent',
                'password': 'password123'
            })
            response = client.post('/courses/new', data={
                'course_name': 'Unauthorized Course',
                'course_code': 'CS888',
                'description': 'Should not be created'
            }, follow_redirects=True)
            
            # Verify course was not created
            unauthorized_course = Course.query.filter_by(course_code='CS888').first()
            assert unauthorized_course is None

    def test_instructor_can_create_course(self, client, instructor_user):
        """Test that instructors can create courses."""
        with client:
            client.post('/login', data={
                'username': 'testinstructor',
                'password': 'password123'
            })
            response = client.post('/courses/new', data={
                'course_name': 'Instructor Course',
                'course_code': 'INST101',
                'description': 'Created by instructor'
            }, follow_redirects=True)
            
            # Verify course was created
            inst_course = Course.query.filter_by(course_code='INST101').first()
            assert inst_course is not None
            assert inst_course.course_name == 'Instructor Course'
