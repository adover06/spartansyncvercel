from datetime import datetime, date, timedelta
import calendar
from flask import render_template, redirect, flash, request, url_for, Response
from flask_login import login_required, current_user

from . import bp
from app import db
from app.models import (
    Classes,
    Course,
    Assignment,
    Submission,
    Announcement,
    RubricCriterion,
    Conversation,
    ConversationParticipant,
    Message,
)
from app.forms import (
    AssignmentForm,
    AnnouncementForm,
    SubmissionForm,
    RubricCriterionForm,
    CourseForm,
    ClassSelectionForm,
)
from app.forms import MessageForm, NewConversationForm
from app.models import User


def _course_choices(include_general=True):
    courses = Course.query.order_by(Course.course_name).all()
    choices = []
    if include_general:
        choices.append((0, "General / All Courses"))
    choices.extend((course.id, course.course_name) for course in courses)
    return choices


def _selected_course_ids(user_id):
    classes_record = Classes.query.filter_by(user=user_id).first()
    if not classes_record or not classes_record.classes:
        return []
    selected = []
    for entry in classes_record.classes:
        if isinstance(entry, int):
            selected.append(entry)
        elif isinstance(entry, str) and entry.isdigit():
            selected.append(int(entry))
        elif isinstance(entry, dict) and "course_id" in entry:
            selected.append(entry["course_id"])
    return selected


def _build_class_cards(user_id, include_grades=False):

    classes_record = Classes.query.filter_by(user=user_id).first()
    if not classes_record or not classes_record.classes:
        return []

    cards = []
    for entry in classes_record.classes:
        if isinstance(entry, dict) and entry.get("title"):
            link = entry.get("link")
            cards.append(
                {
                    "title": entry.get("title"),
                    "course_code": entry.get("course_code", ""),
                    "description": entry.get("description", ""),
                    "link": link,
                    "grade_info": None,
                }
            )
        else:
            course_id = None
            if isinstance(entry, int):
                course_id = entry
            elif isinstance(entry, str) and entry.isdigit():
                course_id = int(entry)
            elif isinstance(entry, dict) and entry.get("id"):
                course_id = entry["id"]

            if course_id:
                course = Course.query.get(course_id)
                if course:
                    grade_info = None
                    if include_grades:
                        grade_info = _calculate_weighted_grade(user_id, course_id)

                    cards.append(
                        {
                            "title": course.course_name,
                            "course_code": course.course_code,
                            "description": course.description or "",
                            "link": url_for("main.course_detail", course_id=course.id),
                            "course_id": course.id,
                            "grade_info": grade_info,
                        }
                    )
    return cards


def _assignment_badge(assignment, submission=None):
    now = datetime.utcnow()
    if not assignment.allow_submissions:
        return {"label": "Closed", "class": "bg-gray-100 text-gray-700"}
    if submission and submission.status == "Graded":
        return {"label": "Graded", "class": "bg-green-100 text-green-700"}
    if submission:
        return {"label": "Submitted", "class": "bg-blue-100 text-blue-700"}
    if assignment.due_date < now:
        return {"label": "Overdue", "class": "bg-red-100 text-red-700"}
    return {"label": "Pending", "class": "bg-yellow-100 text-yellow-700"}


def _has_role(user, *roles):
    return user.is_authenticated and user.role in roles


def _require_roles(*roles):
    if not _has_role(current_user, *roles):
        flash("You do not have permission to perform this action.", "error")
        return False
    return True


def _calculate_weighted_grade(student_id, course_id):

    from flask import current_app

    weights = current_app.config.get('GRADE_WEIGHTS', {
        "homework": 30,
        "exam": 50,
        "project": 20,
    })

    assignments = Assignment.query.filter_by(course_id=course_id).all()
    if not assignments:
        return {'grade': None, 'category_grades': {}, 'has_grades': False}

    # get the submissions for these assignments
    assignment_ids = [a.id for a in assignments]
    submissions = Submission.query.filter(
        Submission.assignment_id.in_(assignment_ids),
        Submission.student_id == student_id,
        Submission.status == "Graded"
    ).all()

    if not submissions:
        return {'grade': None, 'category_grades': {}, 'has_grades': False}

    # map of assignment_id -> submission
    sub_map = {s.assignment_id: s for s in submissions}

    # calculate per category scores
    category_data = {}
    for cat in weights.keys():
        category_data[cat] = {'earned': 0, 'possible': 0}

    for assignment in assignments:
        cat = assignment.category if assignment.category in weights else 'homework'
        sub = sub_map.get(assignment.id)
        if sub and sub.score is not None:
            category_data[cat]['earned'] += sub.score
            category_data[cat]['possible'] += assignment.points

    # calculate the weighted average
    total_weighted = 0
    total_weight_used = 0
    category_grades = {}

    for cat, data in category_data.items():
        if data['possible'] > 0:
            percentage = (data['earned'] / data['possible']) * 100
            category_grades[cat] = {
                'earned': data['earned'],
                'possible': data['possible'],
                'percentage': round(percentage, 1),
            }
            total_weighted += percentage * weights[cat]
            total_weight_used += weights[cat]

    # normalize all the categories if not all the categories have grades in
    if total_weight_used > 0:
        final_grade = total_weighted / total_weight_used
    else:
        final_grade = None

    return {
        'grade': round(final_grade, 1) if final_grade is not None else None,
        'category_grades': category_grades,
        'has_grades': total_weight_used > 0,
    }


@bp.route("/")
@bp.route("/home")
@login_required
def home():
    # get ALL courses
    all_courses = Course.query.order_by(Course.course_name.asc()).all()

    # get enrolled course IDs
    enrolled_ids = set(_selected_course_ids(current_user.id))

    # build course cards with enrollment status
    courses_payload = []
    for course in all_courses:
        is_enrolled = course.id in enrolled_ids
        grade_info = None
        if is_enrolled and current_user.role == "student":
            grade_info = _calculate_weighted_grade(current_user.id, course.id)

        courses_payload.append({
            "title": course.course_name,
            "course_code": course.course_code,
            "description": course.description or "",
            "link": url_for("main.course_detail", course_id=course.id),
            "course_id": course.id,
            "is_enrolled": is_enrolled,
            "grade_info": grade_info,
        })

    # filter assignments by enrolled courses for students
    if current_user.role == "student" and enrolled_ids:
        assignments = Assignment.query.filter(
            (Assignment.course_id.in_(enrolled_ids)) | (Assignment.course_id.is_(None))
        ).order_by(Assignment.due_date.asc()).limit(8).all()

        announcements = Announcement.query.filter(
            (Announcement.course_id.in_(enrolled_ids)) | (Announcement.course_id.is_(None))
        ).order_by(Announcement.created_at.desc()).limit(5).all()
    else:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).limit(8).all()
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    submissions = {}
    if current_user.role == "student":
        user_submissions = Submission.query.filter_by(student_id=current_user.id).all()
        submissions = {sub.assignment_id: sub for sub in user_submissions}

    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submissions.get(assignment.id)
        )

    return render_template(
        'home.html',
        courses=courses_payload,
        assignments=assignments,
        announcements=announcements,
    )


@bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "instructor":
        assignments = Assignment.query.filter_by(
            created_by=current_user.id
        ).order_by(Assignment.due_date).all()

        pending_submissions = Submission.query.join(Assignment).filter(
            Assignment.created_by == current_user.id,
            Submission.status != "Graded",
        ).all()

        return render_template(
            "dashboard.html",
            mode="instructor",
            assignments=assignments,
            pending_submissions=pending_submissions,
        )

    elif current_user.role == "ta":
        ta_course_ids = _selected_course_ids(current_user.id)

        assignments = Assignment.query.filter(
            Assignment.course_id.in_(ta_course_ids)
        ).order_by(Assignment.due_date).all()

        pending_submissions = Submission.query.join(Assignment).filter(
            Assignment.course_id.in_(ta_course_ids),
            Submission.status != "Graded",
        ).all()

        return render_template(
            "dashboard.html",
            mode="instructor",
            assignments=assignments,
            pending_submissions=pending_submissions,
        )

    else:
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
        submissions = Submission.query.filter_by(student_id=current_user.id).all()
        submission_map = {s.assignment_id: s for s in submissions}
        for assignment in assignments:
            assignment.progress_badge = _assignment_badge(
                assignment, submission_map.get(assignment.id)
            )
            assignment.submission = submission_map.get(assignment.id)
        return render_template(
            "dashboard.html",
            mode="student",
            assignments=assignments,
        )


@bp.route("/assignments")
@login_required
def assignment_list():
    assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    submission_map = {}
    if current_user.role == "student":
        submission_map = {
            s.assignment_id: s
            for s in Submission.query.filter_by(student_id=current_user.id).all()
        }
    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submission_map.get(assignment.id)
        )
    return render_template("assignments_list.html", assignments=assignments)


@bp.route("/calendar")
@login_required
def calendar_view():
    """Server-rendered month calendar view of assignments."""
    # allow year/month override via query params
    year = request.args.get("year", type=int) or date.today().year
    month = request.args.get("month", type=int) or date.today().month

    # calculate month range
    first_weekday, num_days = calendar.monthrange(year, month)
    start = datetime(year, month, 1)
    end = datetime(year, month, num_days, 23, 59, 59)

    # fetch assignments; filter by year/month to avoid timezone edge-cases
    all_assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    if current_user.role == "student":
        enrolled = set(_selected_course_ids(current_user.id))
        assignments = [a for a in all_assignments if (a.course_id is None or a.course_id in enrolled) and a.due_date.year == year and a.due_date.month == month]
    else:
        assignments = [a for a in all_assignments if a.due_date.year == year and a.due_date.month == month]

    # group assignments by day (use date to avoid timezone/truncation issues)
    events = {}
    for a in assignments:
        try:
            day = a.due_date.date().day
        except Exception:
            day = a.due_date.day
        events.setdefault(day, []).append(a)

    # sort events for each day by due_date/time
    for lst in events.values():
        lst.sort(key=lambda x: x.due_date)

    # build weeks grid (list of weeks, each week is list of day numbers or None)
    start_offset = first_weekday  # monthrange uses Monday=0
    days = [None] * start_offset + list(range(1, num_days + 1))
    while len(days) % 7 != 0:
        days.append(None)
    weeks = [days[i : i + 7] for i in range(0, len(days), 7)]

    prev_month = (date(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month = (date(year, month, num_days) + timedelta(days=1)).replace(day=1)

    # build a simple color palette per course present in this view
    palette = [
        "#ef4444",
        "#f59e0b",
        "#10b981",
        "#3b82f6",
        "#8b5cf6",
        "#ec4899",
        "#06b6d4",
    ]
    course_ids = []
    course_map = {}
    for a in assignments:
        if a.course and a.course.id not in course_ids:
            course_ids.append(a.course.id)
            course_map[a.course.id] = a.course

    course_colors = {}
    for idx, cid in enumerate(sorted(course_ids)):
        course_colors[cid] = palette[idx % len(palette)]

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        weeks=weeks,
        events=events,
        prev_month=prev_month,
        next_month=next_month,
        course_colors=course_colors,
        course_map=course_map,
    )


@bp.route("/calendar/export")
@login_required
def calendar_export():
    """Export assignments as an iCalendar (.ics) file for the selected month or all upcoming."""
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    # choose assignments: if year/month provided, limit to that month; otherwise upcoming 90 days
    all_assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
    if year and month:
        first_weekday, num_days = calendar.monthrange(year, month)
        start = datetime(year, month, 1)
        end = datetime(year, month, num_days, 23, 59, 59)
    else:
        start = datetime.utcnow()
        end = start + timedelta(days=90)

    if current_user.role == "student":
        enrolled = set(_selected_course_ids(current_user.id))
        assignments = [a for a in all_assignments if (a.course_id is None or a.course_id in enrolled) and start <= a.due_date <= end]
    else:
        assignments = [a for a in all_assignments if start <= a.due_date <= end]

    # build simple ICS
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SpartanSync//Assignments//EN",
    ]

    for a in assignments:
        uid = f"assignment-{a.id}@spartansync.local"
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        dtstart = a.due_date.strftime("%Y%m%dT%H%M%SZ")
        summary = (a.title or "Assignment").replace('\n', ' ').replace(';', ',')
        description = (a.description or '').replace('\n', '\\n').replace(';', ',')
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(lines)

    filename = f"assignments_{year or 'upcoming'}_{month or ''}.ics"
    return Response(ics_content, mimetype="text/calendar", headers={"Content-Disposition": f"attachment; filename={filename}"})


@bp.route("/courses")
@login_required
def courses():
    all_courses = Course.query.order_by(Course.course_name.asc()).all()
    selected_ids = set(_selected_course_ids(current_user.id))
    return render_template(
        "courses.html",
        courses=all_courses,
        selected_ids=selected_ids,
    )


@bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    assignments = Assignment.query.filter_by(course_id=course.id).order_by(Assignment.due_date.asc()).all()
    announcements = Announcement.query.filter_by(course_id=course.id).order_by(Announcement.created_at.desc()).all()

    submission_map = {}
    if current_user.role == "student":
        submission_map = {
            s.assignment_id: s
            for s in Submission.query.filter_by(student_id=current_user.id).all()
        }
    for assignment in assignments:
        assignment.progress_badge = _assignment_badge(
            assignment, submission_map.get(assignment.id)
        )

    return render_template(
        "course_detail.html",
        course=course,
        assignments=assignments,
        announcements=announcements,
    )


@bp.route("/courses/new", methods=["GET", "POST"])
@login_required
def course_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.courses"))

    form = CourseForm()
    if form.validate_on_submit():
        duplicate = Course.query.filter(
            (Course.course_code == form.course_code.data)
            | (Course.course_name == form.course_name.data)
        ).first()
        if duplicate:
            flash("Course with that name or code already exists.", "error")
        else:
            course = Course(
                course_name=form.course_name.data,
                course_code=form.course_code.data,
                description=form.description.data,
            )
            db.session.add(course)
            db.session.commit()
            flash("Course created successfully.", "success")
            return redirect(url_for("main.courses"))

    return render_template("course_form.html", form=form)


@bp.route("/classes/manage", methods=["GET", "POST"])
@login_required
def manage_classes():
    form = ClassSelectionForm()

    # get all courses
    courses = Course.query.order_by(Course.course_name).all()
    if not courses:
        flash("No courses available yet. Please ask an instructor to add one.", "error")
        return redirect(url_for("main.courses"))

    # get currently selected course IDs
    selected_ids = set(_selected_course_ids(current_user.id))

    if request.method == "POST":
        # get selected course IDs from checkboxes
        selected_course_ids = request.form.getlist("courses", type=int)

        record = Classes.query.filter_by(user=current_user.id).first()
        if not record:
            record = Classes(user=current_user.id, classes=selected_course_ids)
            db.session.add(record)
        else:
            record.classes = selected_course_ids
        db.session.commit()
        flash("Enrollment updated successfully.", "success")
        return redirect(url_for("main.home"))

    return render_template("classes_manage.html", form=form, courses=courses, selected_ids=selected_ids)


@bp.route("/assignments/new", methods=["GET", "POST"])
@login_required
def assignment_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.home"))

    form = AssignmentForm()
    form.course.choices = _course_choices()

    if form.validate_on_submit():
        course_id = form.course.data or None
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            points=form.points.data,
            category=form.category.data,
            allow_submissions=form.allow_submissions.data,
            course_id=course_id,
            created_by=current_user.id,
        )
        db.session.add(assignment)
        db.session.flush()

        # seed a simple rubric criterion covering the total points
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title="Overall Quality",
            description="Default rubric criterion",
            max_points=form.points.data,
        )
        db.session.add(criterion)
        db.session.commit()

        flash("Assignment created successfully.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    return render_template("assignment_form.html", form=form)


@bp.route("/assignments/<int:assignment_id>", methods=["GET", "POST"])
@login_required
def assignment_detail(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submission_form = SubmissionForm()
    rubric_form = RubricCriterionForm()
    rubric_form.assignment_id.data = assignment.id

    submission = None
    if current_user.role == "student":
        submission = Submission.query.filter_by(
            assignment_id=assignment.id, student_id=current_user.id
        ).first()
        if submission and submission.rubric_scores:
            submission.rubric_scores = {
                int(k): v for k, v in submission.rubric_scores.items()
            }

    if submission_form.validate_on_submit() and current_user.role == "student":
        if not assignment.allow_submissions:
            flash("Submissions are closed for this assignment.", "error")
        else:
            if submission:
                submission.content = submission_form.content.data
                submission.submitted_at = datetime.utcnow()
                submission.status = "Submitted"
            else:
                submission = Submission(
                    assignment_id=assignment.id,
                    student_id=current_user.id,
                    content=submission_form.content.data,
                    status="Submitted",
                )
                db.session.add(submission)
            db.session.commit()
            flash("Submission saved.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    if rubric_form.validate_on_submit() and current_user.role in ["instructor", "ta"]:
        criterion = RubricCriterion(
            assignment_id=assignment.id,
            title=rubric_form.title.data,
            description=rubric_form.description.data,
            max_points=rubric_form.max_points.data,
        )
        db.session.add(criterion)
        db.session.commit()
        flash("Rubric criterion added.", "success")
        return redirect(url_for("main.assignment_detail", assignment_id=assignment.id))

    if submission:
        submission_form.content.data = submission.content

    submissions = []
    if current_user.role in ["instructor", "ta"]:
        submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
        for sub in submissions:
            if sub.rubric_scores:
                sub.rubric_scores = {int(k): v for k, v in sub.rubric_scores.items()}

    return render_template(
        "assignment_detail.html",
        assignment=assignment,
        submission_form=submission_form,
        rubric_form=rubric_form,
        submission=submission,
        submissions=submissions,
    )


@bp.route("/assignments/<int:assignment_id>/grade", methods=["POST"])
@login_required
def grade_submission(assignment_id):
    if not _require_roles("instructor", "ta"):
        return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

    submission_id = request.form.get("submission_id")
    submission = Submission.query.filter_by(
        id=submission_id, assignment_id=assignment_id
    ).first_or_404()

    rubric_scores = {}
    total = 0
    for criterion in submission.assignment.rubric_criteria:
        field_name = f"criterion_{criterion.id}"
        score_val = request.form.get(field_name, type=int)
        if score_val is None or score_val < 0 or score_val > criterion.max_points:
            flash(f"Invalid points for {criterion.title}.", "error")
            return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))
        rubric_scores[str(criterion.id)] = score_val
        total += score_val

    submission.score = total
    submission.rubric_scores = rubric_scores
    submission.status = "Graded"
    submission.submitted_at = submission.submitted_at or datetime.utcnow()
    db.session.commit()
    flash("Submission graded successfully.", "success")
    return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

@bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
def assignment_delete(assignment_id):
    if not _require_roles("instructor"):
        return redirect(url_for("main.assignment_detail", assignment_id=assignment_id))

    assignment = Assignment.query.get_or_404(assignment_id)
    Submission.query.filter_by(assignment_id=assignment.id).delete()
    RubricCriterion.query.filter_by(assignment_id=assignment.id).delete()
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("main.assignment_list"))


@bp.route("/announcements", methods=["GET"])
@login_required
def announcements():
    notes = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("announcements.html", announcements=notes)


@bp.route("/announcements/<int:announcement_id>")
@login_required
def announcement_detail(announcement_id):
    note = Announcement.query.get_or_404(announcement_id)
    return render_template("announcement_detail.html", announcement=note)


@bp.route("/announcements/new", methods=["GET", "POST"])
@login_required
def announcement_create():
    if not _require_roles("instructor"):
        return redirect(url_for("main.announcements"))

    form = AnnouncementForm()
    form.course.choices = _course_choices()

    if form.validate_on_submit():
        course_id = form.course.data or None
        note = Announcement(
            title=form.title.data,
            body=form.body.data,
            course_id=course_id,
            created_by=current_user.id,
        )
        db.session.add(note)
        db.session.commit()
        flash("Announcement published.", "success")
        return redirect(url_for("main.announcements"))

    return render_template("announcement_form.html", form=form)


@bp.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
@login_required
def announcement_delete(announcement_id):
    if not _require_roles("instructor"):
        return redirect(url_for("main.announcements"))

    note = Announcement.query.get_or_404(announcement_id)
    db.session.delete(note)
    db.session.commit()
    flash("Announcement deleted.", "success")
    return redirect(url_for("main.announcements"))

@bp.route("/study-plan", methods=["GET", "POST"])
@login_required
def study_plan():
    if not _require_roles("student"):
        return redirect(url_for("main.home"))
    try:
        from app.main.gpt_client import ask_chatgpt
    except Exception:
        # If the OpenAI client isn't available provide  fallback
        def ask_chatgpt(question, prompt):
            return "AI service currently unavailable."

    advice = None
    if request.method == "POST":
        assignments = Assignment.query.order_by(Assignment.due_date.asc()).all()
        assignmentPrompt = ""
        for assignment in assignments:
            submitted = Submission.query.filter_by(
                assignment_id=assignment.id,
                student_id=current_user.id
            ).first()
            if not submitted:
                assignmentPrompt += f"- {assignment.title}, due {assignment.due_date.strftime('%Y-%m-%d')}({assignment.points} points)\n"
        question = request.form.get("topics", "").strip()
        
        advice = ask_chatgpt(question, assignmentPrompt)
        return render_template("study_plan.html", advice=advice, prefill=question)
       
    return render_template("study_plan.html", advice=advice, prefill="")


@bp.route("/messages")
@login_required
def messages_inbox():
    """List conversations for current user."""
    parts = ConversationParticipant.query.filter_by(user_id=current_user.id).all()
    conversations = [p.conversation for p in parts]
    # sort by last message time
    conversations.sort(key=lambda c: c.last_message().created_at if c.last_message() else c.created_at, reverse=True)
    # build summary
    summary = []
    for c in conversations:
        last = c.last_message()
        summary.append({
            "conversation": c,
            "last_message": last,
            "unread": c.unread_count_for(current_user.id),
        })

    return render_template("messages/inbox.html", conversations=summary)


@bp.route("/messages/new", methods=["GET", "POST"])
@login_required
def messages_new():
    form = NewConversationForm()
    # populate recipient choices with users (exclude current user)
    users = User.query.order_by(User.username).all()
    form.recipient_id.choices = [(u.id, u.username) for u in users if u.id != current_user.id]
    if form.validate_on_submit():
        recipient_id = int(form.recipient_id.data)
        title = form.title.data or None
        conv = Conversation(title=title, is_group=False)
        db.session.add(conv)
        db.session.flush()

        # add participants: sender and recipient
        sender_part = ConversationParticipant(conversation_id=conv.id, user_id=current_user.id)
        recipient_part = ConversationParticipant(conversation_id=conv.id, user_id=recipient_id)
        db.session.add_all([sender_part, recipient_part])

        # create initial message
        msg = Message(conversation_id=conv.id, sender_id=current_user.id, body=form.body.data)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("main.messages_view", conv_id=conv.id))

    # optionally accept ?recipient_id=.. query param
    rid = request.args.get("recipient_id", type=int)
    if rid and not form.recipient_id.data:
        form.recipient_id.data = rid
    # if user submitted the form but validation failed, show a helpful message
    if request.method == 'POST' and not form.validate_on_submit():
        flash('Could not start conversation. Please select a recipient and enter a message.', 'error')
    return render_template("messages/new.html", form=form)


@bp.route("/messages/<int:conv_id>", methods=["GET", "POST"])
@login_required
def messages_view(conv_id):
    conv = Conversation.query.get_or_404(conv_id)
    # ensure current user is a participant
    part = ConversationParticipant.query.filter_by(conversation_id=conv.id, user_id=current_user.id).first()
    if not part:
        flash("You are not a participant in that conversation.", "error")
        return redirect(url_for("main.messages_inbox"))

    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(conversation_id=conv.id, sender_id=current_user.id, body=form.body.data)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("main.messages_view", conv_id=conv.id))

    # mark read
    from datetime import datetime
    part.last_read_at = datetime.utcnow()
    db.session.commit()

    messages = conv.messages
    return render_template("messages/view.html", conversation=conv, messages=messages, form=form)
