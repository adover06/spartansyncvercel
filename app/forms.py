from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    IntegerField,
    TextAreaField,
    HiddenField,
    SelectMultipleField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, InputRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[
            ('student', 'Student'),
            ('ta', 'Teaching Assistant'),
            ('instructor', 'Instructor'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('Create Account')


class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    course = SelectField('Course', coerce=int, validators=[InputRequired()])
    category = SelectField(
        'Category',
        choices=[
            ('homework', 'Homework'),
            ('exam', 'Exam'),
            ('project', 'Project'),
        ],
        validators=[DataRequired()],
    )
    due_date = DateTimeLocalField('Due Date', validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=0)])
    allow_submissions = BooleanField('Allow Submissions', default=True)
    submit = SubmitField('Save Assignment')


class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    course = SelectField('Course', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Publish')


class SubmissionForm(FlaskForm):
    content = TextAreaField('Submission Notes', validators=[DataRequired()])
    submit = SubmitField('Submit Assignment')


class RubricCriterionForm(FlaskForm):
    assignment_id = HiddenField(validators=[DataRequired()])
    title = StringField('Criterion Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    max_points = IntegerField('Max Points', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Criterion')


class CourseForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    course_code = StringField('Course Code', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Course')


class ClassSelectionForm(FlaskForm):
    courses = SelectMultipleField('Select Classes', coerce=int)
    submit = SubmitField('Save Selection')


class MessageForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class NewConversationForm(FlaskForm):
    # Use a SelectField so users can pick a recipient from a list
    recipient_id = SelectField('Recipient', coerce=int, validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    title = StringField('Title')
    submit = SubmitField('Start Conversation')