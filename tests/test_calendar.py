import pytest


def test_calendar_shows_assignments(client, app, student_user, multiple_assignments, course):
    # disable CSRF for test client
    app.config['WTF_CSRF_ENABLED'] = False
    # ensure the student is enrolled in the course so they see events
    from app.models import Classes
    with app.app_context():
        record = Classes(user=student_user.id, classes=[course.id])
        from app import db
        db.session.add(record)
        db.session.commit()

    # login as the test student
    client.post('/login', data={'username': 'teststudent', 'password': 'password123'}, follow_redirects=True)
    # request the month matching the first fixture assignment to ensure consistency
    first = multiple_assignments[0]
    year = first.due_date.year
    month = first.due_date.month
    res = client.get(f'/calendar?year={year}&month={month}', follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    # the assignments created by the fixtures should appear
    assert 'Assignment 1' in html or 'Assignment 2' in html or 'Assignment 3' in html
    # legend should include the course code
    assert 'CS101' in html
    # calendar wrapper styles applied
    assert 'bg-white' in html and ('rounded' in html or 'shadow' in html)


def test_calendar_export_contains_events(client, app, student_user, multiple_assignments, course):
    app.config['WTF_CSRF_ENABLED'] = False
    # enroll student
    from app.models import Classes
    with app.app_context():
        record = Classes(user=student_user.id, classes=[course.id])
        from app import db
        db.session.add(record)
        db.session.commit()

    client.post('/login', data={'username': 'teststudent', 'password': 'password123'}, follow_redirects=True)
    first = multiple_assignments[0]
    year = first.due_date.year
    month = first.due_date.month
    res = client.get(f'/calendar/export?year={year}&month={month}', follow_redirects=True)
    assert res.status_code == 200
    ics = res.get_data(as_text=True)
    assert 'BEGIN:VCALENDAR' in ics
    # At least one test fixture assignment should be present in the ICS
    assert 'Assignment 1' in ics or 'Assignment 2' in ics or 'Assignment 3' in ics
    # ICS should contain DTSTART entries
    assert 'DTSTART' in ics
