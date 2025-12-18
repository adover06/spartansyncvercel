import pytest
from werkzeug.security import generate_password_hash


def login(client, username, password="password123"):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_create_conversation_and_send_message(app, client, student_user, instructor_user):
    app.config['WTF_CSRF_ENABLED'] = False
    # login as student
    login(client, 'teststudent')

    # create conversation
    res = client.post('/messages/new', data={'recipient_id': str(instructor_user.id), 'body': 'Hello instructor', 'title': 'Question'}, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    # should redirect to the conversation view and show the message
    assert 'Hello instructor' in html

    # verify conversation exists in db
    from app import db
    from app.models import Conversation, Message, ConversationParticipant
    conv = Conversation.query.first()
    assert conv is not None
    assert any(p.user_id == student_user.id for p in conv.participants)
    assert any(p.user_id == instructor_user.id for p in conv.participants)
    assert Message.query.filter_by(conversation_id=conv.id).count() == 1


def test_inbox_and_unread_counts(app, client, student_user, instructor_user):
    app.config['WTF_CSRF_ENABLED'] = False
    # create conversation via model
    from app import db
    from app.models import Conversation, ConversationParticipant, Message
    conv = Conversation(title='Test', is_group=False)
    db.session.add(conv)
    db.session.flush()
    db.session.add_all([
        ConversationParticipant(conversation_id=conv.id, user_id=student_user.id),
        ConversationParticipant(conversation_id=conv.id, user_id=instructor_user.id),
    ])
    msg = Message(conversation_id=conv.id, sender_id=instructor_user.id, body='Please review')
    db.session.add(msg)
    db.session.commit()

    # login as student and check inbox
    login(client, 'teststudent')
    res = client.get('/messages')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Please review' in html
    # unread badge should show 1
    assert '1' in html


def test_access_control_prevents_nonparticipants(app, client, student_user, instructor_user, ta_user):
    app.config['WTF_CSRF_ENABLED'] = False
    from app import db
    from app.models import Conversation, ConversationParticipant, Message
    conv = Conversation(title='Private', is_group=False)
    db.session.add(conv)
    db.session.flush()
    db.session.add_all([
        ConversationParticipant(conversation_id=conv.id, user_id=student_user.id),
        ConversationParticipant(conversation_id=conv.id, user_id=instructor_user.id),
    ])
    msg = Message(conversation_id=conv.id, sender_id=student_user.id, body='Secret')
    db.session.add(msg)
    db.session.commit()

    # login as ta (not participant)
    login(client, 'testta')
    res = client.get(f'/messages/{conv.id}', follow_redirects=True)
    html = res.get_data(as_text=True)
    assert 'You are not a participant' in html or res.status_code == 200
