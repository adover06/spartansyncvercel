import pytest
from datetime import datetime, timedelta
from app import db
from app.models import Classes, Course, Assignment, Submission, RubricCriterion, Announcement


def login(client, username, password="password123"):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_selected_course_ids_various_entries(app_context):
    # create some courses
    c1 = Course(course_name='C1', course_code='C1')
    c2 = Course(course_name='C2', course_code='C2')
    c3 = Course(course_name='C3', course_code='C3')
    db.session.add_all([c1, c2, c3])
    db.session.commit()

    # create classes record with mixed entries
    rec = Classes(user=1, classes=[c1.id, str(c2.id), {'course_id': c3.id}])
    db.session.add(rec)
    db.session.commit()

    from app.main.routes import _selected_course_ids
    ids = _selected_course_ids(1)
    assert set(ids) == {c1.id, c2.id, c3.id}


def test_assignment_badge_variants(app_context):
    from app.main.routes import _assignment_badge

    now = datetime.utcnow()
    a_future = Assignment(title='F', description='', due_date=now + timedelta(days=2), points=10, allow_submissions=True, created_by=1)
    a_past = Assignment(title='P', description='', due_date=now - timedelta(days=2), points=10, allow_submissions=True, created_by=1)
    a_closed = Assignment(title='C', description='', due_date=now + timedelta(days=2), points=10, allow_submissions=False, created_by=1)
    db.session.add_all([a_future, a_past, a_closed])
    db.session.commit()

    # no submission => future pending
    badge = _assignment_badge(a_future, None)
    assert badge['label'] == 'Pending'

    # past => overdue
    badge = _assignment_badge(a_past, None)
    assert badge['label'] == 'Overdue'

    # closed
    badge = _assignment_badge(a_closed, None)
    assert badge['label'] == 'Closed'

    # submitted and graded
    sub = Submission(assignment_id=a_future.id, student_id=2, content='x', status='Graded', score=8)
    db.session.add(sub)
    db.session.commit()
    badge = _assignment_badge(a_future, sub)
    assert badge['label'] == 'Graded'


def test_calculate_weighted_grade_basic(app_context, student_user, instructor_user):
    # create course and assignments
    course = Course(course_name='Calc', course_code='CALC')
    db.session.add(course)
    db.session.commit()

    a1 = Assignment(title='A1', description='', due_date=datetime.utcnow() + timedelta(days=1), points=50, category='homework', created_by=instructor_user.id, course_id=course.id)
    a2 = Assignment(title='A2', description='', due_date=datetime.utcnow() + timedelta(days=2), points=50, category='exam', created_by=instructor_user.id, course_id=course.id)
    db.session.add_all([a1, a2])
    db.session.commit()

    # student graded submissions
    s1 = Submission(assignment_id=a1.id, student_id=student_user.id, status='Graded', score=45)
    s2 = Submission(assignment_id=a2.id, student_id=student_user.id, status='Graded', score=40)
    db.session.add_all([s1, s2])
    db.session.commit()

    from app.main.routes import _calculate_weighted_grade
    res = _calculate_weighted_grade(student_user.id, course.id)
    assert res['has_grades'] is True
    assert 'homework' in res['category_grades']
    assert 'exam' in res['category_grades']


def test_manage_classes_post_and_home_update(client, app_context, student_user, course):
    # log in and post selection
    login(client, 'teststudent')
    res = client.post('/classes/manage', data={'courses': [str(course.id)]}, follow_redirects=True)
    assert res.status_code == 200
    # Classes record should exist
    rec = Classes.query.filter_by(user=student_user.id).first()
    assert rec is not None


def test_assignment_submission_and_grading_flow(client, app_context, student_user, instructor_user, course):
    # instructor creates assignment
    login(client, 'testinstructor')
    due_date = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
    client.post('/assignments/new', data={'title': 'Flow', 'description': 'D', 'course': str(course.id), 'due_date': due_date, 'points': 20, 'allow_submissions': 'y', 'category': 'homework'}, follow_redirects=True)
    assignment = Assignment.query.filter_by(title='Flow').first()
    assert assignment is not None

    # student submits
    login(client, 'teststudent')
    res = client.post(f'/assignments/{assignment.id}', data={'content': 'My work'}, follow_redirects=True)
    assert b'Submission saved' in res.data
    sub = Submission.query.filter_by(assignment_id=assignment.id, student_id=student_user.id).first()
    assert sub is not None

    # instructor grades
    login(client, 'testinstructor')
    # get rubric criterion
    crit = RubricCriterion.query.filter_by(assignment_id=assignment.id).first()
    assert crit is not None
    data = {'submission_id': sub.id, f'criterion_{crit.id}': str(10)}
    res = client.post(f'/assignments/{assignment.id}/grade', data=data, follow_redirects=True)
    assert b'Submission graded successfully' in res.data
    sub = Submission.query.get(sub.id)
    assert sub.status == 'Graded'


def test_grade_submission_invalid_points(client, app_context, student_user, instructor_user, course):
    login(client, 'testinstructor')
    due_date = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
    client.post('/assignments/new', data={'title': 'Invalid', 'description': 'D', 'course': str(course.id), 'due_date': due_date, 'points': 20, 'allow_submissions': 'y', 'category': 'homework'}, follow_redirects=True)
    assignment = Assignment.query.filter_by(title='Invalid').first()
    # student submits
    login(client, 'teststudent')
    client.post(f'/assignments/{assignment.id}', data={'content': 'Work'}, follow_redirects=True)
    sub = Submission.query.filter_by(assignment_id=assignment.id).first()
    # instructor posts invalid points
    login(client, 'testinstructor')
    crit = RubricCriterion.query.filter_by(assignment_id=assignment.id).first()
    res = client.post(f'/assignments/{assignment.id}/grade', data={'submission_id': sub.id, f'criterion_{crit.id}': str(999)}, follow_redirects=True)
    assert b'Invalid points' in res.data


def test_announcement_create_and_delete_permissions(client, app_context, student_user, instructor_user, course):
    # student cannot create
    login(client, 'teststudent')
    res = client.post('/announcements/new', data={'title': 'N', 'body': 'B', 'course': course.id}, follow_redirects=True)
    assert b'You do not have permission' in res.data or res.status_code == 200

    # instructor can create and delete
    login(client, 'testinstructor')
    res = client.post('/announcements/new', data={'title': 'N', 'body': 'B', 'course': course.id}, follow_redirects=True)
    assert b'Announcement published' in res.data
    ann = Announcement.query.filter_by(title='N').first()
    assert ann is not None
    # delete
    res = client.post(f'/announcements/{ann.id}/delete', follow_redirects=True)
    assert b'Announcement deleted' in res.data


def test_study_plan_post_with_mock(client, app_context, student_user, monkeypatch):
    # create an assignment to include in prompt
    # ensure the OpenAI client doesn't raise during import by setting a dummy key
    monkeypatch.setenv('OPENAI_API_KEY', 'test')
    from app.main import gpt_client

    def fake_ask(q, p):
        return 'Plan: do X'

    monkeypatch.setattr(gpt_client, 'ask_chatgpt', fake_ask)

    login(client, 'teststudent')
    res = client.post('/study-plan', data={'topics': 'focus on testing'}, follow_redirects=True)
    assert b'Plan: do X' in res.data


def test_study_plan_fallback_when_unavailable(client, app_context, student_user, monkeypatch):
    # Force import to fail by removing module
    import sys
    if 'app.main.gpt_client' in sys.modules:
        del sys.modules['app.main.gpt_client']

    login(client, 'teststudent')
    res = client.post('/study-plan', data={'topics': 'x'}, follow_redirects=True)
    assert b'AI service currently unavailable.' in res.data


def test_config_values():
    import app.config as config
    # weights sum to 100
    assert sum(config.Config.GRADE_WEIGHTS.values()) == 100
    keys = {k for k, _ in config.Config.ASSIGNMENT_CATEGORIES}
    assert keys == set(config.Config.GRADE_WEIGHTS.keys())


def test_gpt_client_ask(monkeypatch):
    # ensure env var present for import
    monkeypatch.setenv('OPENAI_API_KEY', 'test')
    import importlib
    import app.main.gpt_client as gpt_client

    class DummyChoice:
        def __init__(self, content):
            self.message = type('M', (), {'content': content})

    class DummyResp:
        def __init__(self, content):
            self.choices = [DummyChoice(content)]

    def fake_create(**kwargs):
        return DummyResp('Generated plan')

    # monkeypatch the nested client.chat.completions.create
    monkeypatch.setattr(gpt_client.client.chat.completions, 'create', fake_create)
    out = gpt_client.ask_chatgpt('q', 'assigns')
    assert out == 'Generated plan'
