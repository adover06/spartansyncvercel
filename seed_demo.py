'''
Demo Data Seeding Script for SpartanSync

This script creates demo data including:
- 15 users (5 students, 5 instructors, 5 TAs)
- 5 courses (Physics, Math, CS, Chemistry, English)
- 15-20 assignments with rubrics
- Student submissions with varied states
- Announcements
- Message conversations


    python seed_demo.py
    python seed_demo.py --reset
    flask seed-demo
    flask seed-demo --reset
'''

import sys
import argparse
import random
from datetime import datetime, timedelta

from app import create_app, db
from app.models import (
    User, Course, Assignment, Submission, Announcement,
    RubricCriterion, Classes, Conversation, ConversationParticipant, Message
)


def clear_demo_data():
    print("Clearing existing demo data...")

    # Find all demo users
    demo_users = User.query.filter(User.username.like('demo-%')).all()
    demo_user_ids = [u.id for u in demo_users]

    if not demo_users:
        print("No demo data found.")
        return

    # Delete related data
    # Submissions by demo students
    Submission.query.filter(Submission.student_id.in_(demo_user_ids)).delete(synchronize_session=False)

    # Assignments created by demo instructors
    demo_assignments = Assignment.query.filter(Assignment.created_by.in_(demo_user_ids)).all()
    demo_assignment_ids = [a.id for a in demo_assignments]

    # Rubric criteria for demo assignments
    RubricCriterion.query.filter(RubricCriterion.assignment_id.in_(demo_assignment_ids)).delete(synchronize_session=False)

    # Delete demo assignments
    Assignment.query.filter(Assignment.id.in_(demo_assignment_ids)).delete(synchronize_session=False)

    # Announcements created by demo users
    Announcement.query.filter(Announcement.created_by.in_(demo_user_ids)).delete(synchronize_session=False)

    # Enrollments for demo users
    Classes.query.filter(Classes.user.in_(demo_user_ids)).delete(synchronize_session=False)

    # Messages and conversations involving demo users
    demo_conversations = Conversation.query.join(ConversationParticipant).filter(
        ConversationParticipant.user_id.in_(demo_user_ids)
    ).all()
    demo_conversation_ids = [c.id for c in demo_conversations]

    Message.query.filter(Message.conversation_id.in_(demo_conversation_ids)).delete(synchronize_session=False)
    ConversationParticipant.query.filter(ConversationParticipant.conversation_id.in_(demo_conversation_ids)).delete(synchronize_session=False)
    Conversation.query.filter(Conversation.id.in_(demo_conversation_ids)).delete(synchronize_session=False)

    # Delete demo courses (identified by course codes)
    demo_course_codes = ['PHYS101', 'MATH201', 'CS101', 'CHEM150', 'ENG102']
    Course.query.filter(Course.course_code.in_(demo_course_codes)).delete(synchronize_session=False)

    # Finally, delete demo users
    User.query.filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)

    db.session.commit()
    print(f"   ✓ Cleared {len(demo_users)} demo users and all associated data")


def seed_users():
    """Create demo users: 5 students, 5 instructors, 5 TAs."""
    print("\n👥 Creating demo users...")

    users = {}

    # Students
    for i in range(1, 6):
        username = f"demo-student{i}"
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                email=f"demo-student{i}@spartansync.demo",
                role="student"
            )
            user.set_password("demo")
            db.session.add(user)
            users[f"student{i}"] = user
            print(f"   ✓ Created student: {username}")
        else:
            users[f"student{i}"] = User.query.filter_by(username=username).first()
            print(f"   ⚠ Student already exists: {username}")

    # Instructors
    subjects = ['physics', 'math', 'cs', 'chem', 'eng']
    for subject in subjects:
        username = f"demo-{subject}-instructor"
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                email=f"demo-{subject}-instructor@spartansync.demo",
                role="instructor"
            )
            user.set_password("demo")
            db.session.add(user)
            users[f"{subject}_instructor"] = user
            print(f"   ✓ Created instructor: {username}")
        else:
            users[f"{subject}_instructor"] = User.query.filter_by(username=username).first()
            print(f"   ⚠ Instructor already exists: {username}")

    # TAs
    for subject in subjects:
        username = f"demo-{subject}-ta"
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                email=f"demo-{subject}-ta@spartansync.demo",
                role="ta"
            )
            user.set_password("demo")
            db.session.add(user)
            users[f"{subject}_ta"] = user
            print(f"   ✓ Created TA: {username}")
        else:
            users[f"{subject}_ta"] = User.query.filter_by(username=username).first()
            print(f"   ⚠ TA already exists: {username}")

    db.session.commit()
    print(f"   📊 Total users: {len(users)}")

    return users


def seed_courses(instructors):
    """Create 5 demo courses, one per subject."""
    print("\n📚 Creating demo courses...")

    course_data = [
        {
            'code': 'PHYS101',
            'name': 'Introduction to Physics',
            'description': 'Explore the fundamental principles of physics including mechanics, thermodynamics, and electromagnetism.',
            'instructor_key': 'physics_instructor'
        },
        {
            'code': 'MATH201',
            'name': 'Calculus II',
            'description': 'Advanced calculus covering integration techniques, sequences, series, and multivariable calculus.',
            'instructor_key': 'math_instructor'
        },
        {
            'code': 'CS101',
            'name': 'Introduction to Programming',
            'description': 'Learn programming fundamentals using Python, including data structures, algorithms, and problem-solving.',
            'instructor_key': 'cs_instructor'
        },
        {
            'code': 'CHEM150',
            'name': 'General Chemistry',
            'description': 'Study atomic structure, chemical bonding, reactions, and laboratory techniques.',
            'instructor_key': 'chem_instructor'
        },
        {
            'code': 'ENG102',
            'name': 'Composition and Literature',
            'description': 'Develop writing skills through analysis of literary works and composition practice.',
            'instructor_key': 'eng_instructor'
        }
    ]

    courses = {}
    for data in course_data:
        existing = Course.query.filter_by(course_code=data['code']).first()
        if not existing:
            course = Course(
                course_code=data['code'],
                course_name=data['name'],
                description=data['description']
            )
            db.session.add(course)
            courses[data['instructor_key']] = course
            print(f"   ✓ Created course: {data['code']} - {data['name']}")
        else:
            courses[data['instructor_key']] = existing
            print(f"   ⚠ Course already exists: {data['code']}")

    db.session.commit()
    print(f"   📊 Total courses: {len(courses)}")

    return courses


def seed_assignments(courses, instructors):
    """Create assignments for each course (3-4 per course)."""
    print("\n📝 Creating demo assignments...")

    # Assignment templates for each subject
    assignment_templates = {
        'physics_instructor': [
            {
                'title': 'Kinematics Problem Set',
                'description': 'Solve problems involving motion, velocity, and acceleration. Show all work and include units.',
                'category': 'homework',
                'points': 100,
                'days_offset': -14,  # 2 weeks ago
                'rubrics': [
                    {'title': 'Correctness', 'description': 'Accuracy of solutions', 'max_points': 60},
                    {'title': 'Work Shown', 'description': 'Clear step-by-step work', 'max_points': 40}
                ]
            },
            {
                'title': 'Force and Motion Lab',
                'description': 'Complete the lab experiment on Newton\'s Laws. Submit lab report with data and analysis.',
                'category': 'homework',
                'points': 100,
                'days_offset': 7,
                'rubrics': [
                    {'title': 'Data Collection', 'description': 'Accuracy and completeness of data', 'max_points': 30},
                    {'title': 'Analysis', 'description': 'Quality of analysis and conclusions', 'max_points': 50},
                    {'title': 'Presentation', 'description': 'Organization and clarity', 'max_points': 20}
                ]
            },
            {
                'title': 'Midterm Exam',
                'description': 'Comprehensive exam covering chapters 1-5. Bring a calculator and formula sheet.',
                'category': 'exam',
                'points': 150,
                'days_offset': -7,
                'rubrics': [
                    {'title': 'Problem Solving', 'description': 'Ability to solve physics problems', 'max_points': 100},
                    {'title': 'Conceptual Understanding', 'description': 'Understanding of concepts', 'max_points': 50}
                ]
            },
            {
                'title': 'Pendulum Motion Project',
                'description': 'Build and analyze a pendulum. Create a presentation showing your findings.',
                'category': 'project',
                'points': 200,
                'days_offset': 21,
                'rubrics': [
                    {'title': 'Experimental Design', 'description': 'Quality of experimental setup', 'max_points': 60},
                    {'title': 'Data Analysis', 'description': 'Thoroughness of analysis', 'max_points': 80},
                    {'title': 'Presentation', 'description': 'Quality of final presentation', 'max_points': 60}
                ]
            }
        ],
        'math_instructor': [
            {
                'title': 'Integration Techniques',
                'description': 'Complete problems 1-30 from Chapter 7. Use various integration methods.',
                'category': 'homework',
                'points': 100,
                'days_offset': -10,
                'rubrics': [
                    {'title': 'Technique Application', 'description': 'Correct use of integration methods', 'max_points': 60},
                    {'title': 'Accuracy', 'description': 'Correctness of final answers', 'max_points': 40}
                ]
            },
            {
                'title': 'Series and Sequences',
                'description': 'Analyze convergence and divergence of given series. Show all tests used.',
                'category': 'homework',
                'points': 100,
                'days_offset': 5,
                'rubrics': [
                    {'title': 'Test Selection', 'description': 'Appropriate test choices', 'max_points': 40},
                    {'title': 'Correctness', 'description': 'Accuracy of conclusions', 'max_points': 60}
                ]
            },
            {
                'title': 'Calculus II Final Exam',
                'description': 'Cumulative final exam covering all course material.',
                'category': 'exam',
                'points': 200,
                'days_offset': 14,
                'rubrics': [
                    {'title': 'Problem Solving', 'description': 'Application of calculus techniques', 'max_points': 120},
                    {'title': 'Conceptual Understanding', 'description': 'Understanding of theory', 'max_points': 80}
                ]
            },
            {
                'title': 'Real-World Application Project',
                'description': 'Apply calculus to a real-world problem of your choice. Write a report.',
                'category': 'project',
                'points': 150,
                'days_offset': 28,
                'rubrics': [
                    {'title': 'Problem Selection', 'description': 'Appropriateness of problem', 'max_points': 30},
                    {'title': 'Mathematical Rigor', 'description': 'Correct application of calculus', 'max_points': 80},
                    {'title': 'Communication', 'description': 'Clarity of written report', 'max_points': 40}
                ]
            }
        ],
        'cs_instructor': [
            {
                'title': 'Python Basics - Variables and Loops',
                'description': 'Write Python programs to solve the given problems using loops and conditionals.',
                'category': 'homework',
                'points': 100,
                'days_offset': -21,
                'rubrics': [
                    {'title': 'Code Correctness', 'description': 'Programs run without errors', 'max_points': 50},
                    {'title': 'Code Style', 'description': 'Following Python conventions', 'max_points': 30},
                    {'title': 'Documentation', 'description': 'Comments and docstrings', 'max_points': 20}
                ]
            },
            {
                'title': 'Data Structures Implementation',
                'description': 'Implement linked lists, stacks, and queues from scratch in Python.',
                'category': 'homework',
                'points': 150,
                'days_offset': 3,
                'rubrics': [
                    {'title': 'Correctness', 'description': 'Proper implementation', 'max_points': 80},
                    {'title': 'Efficiency', 'description': 'Time and space complexity', 'max_points': 40},
                    {'title': 'Testing', 'description': 'Comprehensive test cases', 'max_points': 30}
                ]
            },
            {
                'title': 'Programming Midterm',
                'description': 'Timed coding exam testing your knowledge of Python and algorithms.',
                'category': 'exam',
                'points': 150,
                'days_offset': -5,
                'rubrics': [
                    {'title': 'Problem Solving', 'description': 'Ability to solve coding challenges', 'max_points': 100},
                    {'title': 'Code Quality', 'description': 'Readability and efficiency', 'max_points': 50}
                ]
            },
            {
                'title': 'Final Project - Web Application',
                'description': 'Build a complete web application using Flask. Must include database and user authentication.',
                'category': 'project',
                'points': 250,
                'days_offset': 30,
                'rubrics': [
                    {'title': 'Functionality', 'description': 'All required features work', 'max_points': 100},
                    {'title': 'Code Quality', 'description': 'Well-organized and documented', 'max_points': 70},
                    {'title': 'User Interface', 'description': 'Usability and design', 'max_points': 50},
                    {'title': 'Database Design', 'description': 'Proper schema and queries', 'max_points': 30}
                ]
            }
        ],
        'chem_instructor': [
            {
                'title': 'Chemical Bonding Problems',
                'description': 'Complete problem set on ionic and covalent bonding, Lewis structures.',
                'category': 'homework',
                'points': 100,
                'days_offset': -8,
                'rubrics': [
                    {'title': 'Lewis Structures', 'description': 'Correct structures drawn', 'max_points': 50},
                    {'title': 'Bond Types', 'description': 'Identification and explanation', 'max_points': 50}
                ]
            },
            {
                'title': 'Stoichiometry Exam',
                'description': 'Exam covering molar calculations, limiting reagents, and percent yield.',
                'category': 'exam',
                'points': 150,
                'days_offset': 10,
                'rubrics': [
                    {'title': 'Calculations', 'description': 'Accuracy of quantitative problems', 'max_points': 100},
                    {'title': 'Conceptual Questions', 'description': 'Understanding of theory', 'max_points': 50}
                ]
            },
            {
                'title': 'Lab Safety and Techniques Project',
                'description': 'Create a comprehensive lab safety guide and demonstrate proper techniques.',
                'category': 'project',
                'points': 150,
                'days_offset': 25,
                'rubrics': [
                    {'title': 'Completeness', 'description': 'All safety topics covered', 'max_points': 50},
                    {'title': 'Accuracy', 'description': 'Correct information and procedures', 'max_points': 60},
                    {'title': 'Presentation', 'description': 'Organization and clarity', 'max_points': 40}
                ]
            }
        ],
        'eng_instructor': [
            {
                'title': 'Literary Analysis Essay',
                'description': 'Write a 5-page analysis of one of the assigned novels. Use MLA format.',
                'category': 'homework',
                'points': 100,
                'days_offset': -12,
                'rubrics': [
                    {'title': 'Thesis and Argument', 'description': 'Strength of central argument', 'max_points': 35},
                    {'title': 'Evidence and Analysis', 'description': 'Use of textual evidence', 'max_points': 40},
                    {'title': 'Writing Quality', 'description': 'Grammar, style, organization', 'max_points': 25}
                ]
            },
            {
                'title': 'Poetry Analysis Exam',
                'description': 'In-class exam analyzing provided poems. Identify literary devices and themes.',
                'category': 'exam',
                'points': 150,
                'days_offset': 8,
                'rubrics': [
                    {'title': 'Literary Device Identification', 'description': 'Recognition of techniques', 'max_points': 70},
                    {'title': 'Interpretation', 'description': 'Understanding of meaning', 'max_points': 80}
                ]
            },
            {
                'title': 'Research Paper Project',
                'description': 'Write a 10-page research paper on a literary topic of your choice. Requires 8+ sources.',
                'category': 'project',
                'points': 200,
                'days_offset': 35,
                'rubrics': [
                    {'title': 'Research Quality', 'description': 'Quality and relevance of sources', 'max_points': 50},
                    {'title': 'Argumentation', 'description': 'Strength of thesis and argument', 'max_points': 70},
                    {'title': 'Writing and Citations', 'description': 'Writing quality and proper MLA', 'max_points': 80}
                ]
            }
        ]
    }

    assignments = []
    now = datetime.utcnow()

    for instructor_key, templates in assignment_templates.items():
        course = courses[instructor_key]
        instructor = instructors[instructor_key]

        for template in templates:
            due_date = now + timedelta(days=template['days_offset'])

            assignment = Assignment(
                title=template['title'],
                description=template['description'],
                due_date=due_date,
                points=template['points'],
                category=template['category'],
                status='Published',
                allow_submissions=True,
                course_id=course.id,
                created_by=instructor.id
            )
            db.session.add(assignment)
            db.session.flush()  # Get assignment ID

            # Add rubric criteria
            for rubric_data in template['rubrics']:
                rubric = RubricCriterion(
                    assignment_id=assignment.id,
                    title=rubric_data['title'],
                    description=rubric_data['description'],
                    max_points=rubric_data['max_points']
                )
                db.session.add(rubric)

            assignments.append(assignment)
            print(f"   ✓ Created assignment: {template['title']} ({course.course_code})")

    db.session.commit()
    print(f"   📊 Total assignments: {len(assignments)}")

    return assignments


def seed_enrollments(students, tas, courses):
    """Create enrollment records for students and TAs."""
    print("\n🎓 Creating enrollments...")

    # Student enrollment mapping (each student in 3 courses)
    student_enrollments = {
        'student1': ['physics_instructor', 'math_instructor', 'cs_instructor'],  # PHYS, MATH, CS
        'student2': ['math_instructor', 'cs_instructor', 'chem_instructor'],      # MATH, CS, CHEM
        'student3': ['cs_instructor', 'chem_instructor', 'eng_instructor'],       # CS, CHEM, ENG
        'student4': ['physics_instructor', 'chem_instructor', 'eng_instructor'],  # PHYS, CHEM, ENG
        'student5': ['physics_instructor', 'math_instructor', 'eng_instructor']   # PHYS, MATH, ENG
    }

    # TA enrollment mapping (each TA in one course)
    ta_enrollments = {
        'physics_ta': ['physics_instructor'],
        'math_ta': ['math_instructor'],
        'cs_ta': ['cs_instructor'],
        'chem_ta': ['chem_instructor'],
        'eng_ta': ['eng_instructor']
    }

    enrollment_count = 0

    # Enroll students
    for student_key, course_keys in student_enrollments.items():
        student = students[student_key]
        course_ids = [courses[ck].id for ck in course_keys]

        existing = Classes.query.filter_by(user=student.id).first()
        if not existing:
            enrollment = Classes(
                user=student.id,
                classes=course_ids
            )
            db.session.add(enrollment)
            enrollment_count += 1
            print(f"   ✓ Enrolled {student.username} in {len(course_ids)} courses")
        else:
            print(f"   ⚠ {student.username} already enrolled")

    # Enroll TAs
    for ta_key, course_keys in ta_enrollments.items():
        ta = tas[ta_key]
        course_ids = [courses[ck].id for ck in course_keys]

        existing = Classes.query.filter_by(user=ta.id).first()
        if not existing:
            enrollment = Classes(
                user=ta.id,
                classes=course_ids
            )
            db.session.add(enrollment)
            enrollment_count += 1
            print(f"   ✓ Enrolled {ta.username} in {len(course_ids)} course(s)")
        else:
            print(f"   ⚠ {ta.username} already enrolled")

    db.session.commit()
    print(f"   📊 Total enrollments: {enrollment_count}")


def seed_submissions(assignments, students, courses):
    """Create submissions for assignments with varied states."""
    print("\n📤 Creating submissions...")

    # Get student enrollments to only submit for enrolled courses
    student_course_map = {
        'student1': [courses['physics_instructor'].id, courses['math_instructor'].id, courses['cs_instructor'].id],
        'student2': [courses['math_instructor'].id, courses['cs_instructor'].id, courses['chem_instructor'].id],
        'student3': [courses['cs_instructor'].id, courses['chem_instructor'].id, courses['eng_instructor'].id],
        'student4': [courses['physics_instructor'].id, courses['chem_instructor'].id, courses['eng_instructor'].id],
        'student5': [courses['physics_instructor'].id, courses['math_instructor'].id, courses['eng_instructor'].id]
    }

    submission_count = 0
    graded_count = 0
    now = datetime.utcnow()

    for assignment in assignments:
        # Find eligible students (enrolled in this assignment's course)
        eligible_students = []
        for student_key, course_ids in student_course_map.items():
            if assignment.course_id in course_ids:
                eligible_students.append(students[student_key])

        # 60% submission rate
        num_submissions = max(1, int(len(eligible_students) * 0.6))
        submitting_students = random.sample(eligible_students, num_submissions)

        for student in submitting_students:
            # Submission content based on assignment type
            content_templates = {
                'homework': [
                    'Completed all problems. Please see attached work.',
                    'Finished the assignment. All calculations are shown step by step.',
                    'Here is my solution to the problem set.',
                ],
                'exam': [
                    'Exam completed to the best of my ability.',
                    'Finished within the time limit.',
                ],
                'project': [
                    'Project submission with all required components. See documentation for details.',
                    'Completed project including code, analysis, and presentation materials.',
                    'Final project submission. All requirements met.',
                ]
            }

            content = random.choice(content_templates.get(assignment.category, ['Assignment completed.']))

            # Vary submission time
            if assignment.due_date < now:
                # Past assignments: submitted before due date
                days_before_due = random.randint(1, 7)
                submitted_at = assignment.due_date - timedelta(days=days_before_due)
            else:
                # Future assignments: not submitted yet, skip
                continue

            # 40% of submissions are graded
            is_graded = random.random() < 0.4

            if is_graded:
                # Get rubric criteria for scoring
                rubrics = RubricCriterion.query.filter_by(assignment_id=assignment.id).all()
                rubric_scores = {}
                total_score = 0

                # Generate scores (70-100% of max for each criterion)
                for rubric in rubrics:
                    score = int(rubric.max_points * random.uniform(0.7, 1.0))
                    rubric_scores[str(rubric.id)] = score
                    total_score += score

                submission = Submission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    submitted_at=submitted_at,
                    content=content,
                    status='Graded',
                    score=total_score,
                    rubric_scores=rubric_scores
                )
                graded_count += 1
            else:
                submission = Submission(
                    assignment_id=assignment.id,
                    student_id=student.id,
                    submitted_at=submitted_at,
                    content=content,
                    status='Submitted'
                )

            db.session.add(submission)
            submission_count += 1

    db.session.commit()
    print(f"Created {submission_count} submissions ({graded_count} graded)")


def seed_announcements(courses, instructors):
    """Create announcements for each course."""
    print("\nCreating announcements...")

    announcement_templates = {
        'physics_instructor': [
            {
                'title': 'Welcome to Physics!',
                'body': 'Welcome to Introduction to Physics! We will explore the fundamental laws that govern our universe. Check the syllabus for office hours and exam dates.',
                'days_ago': 30,
                'course': True
            },
            {
                'title': 'Lab Safety Reminder',
                'body': 'Please review the lab safety guidelines before our next lab session. Safety goggles and closed-toe shoes are required.',
                'days_ago': 15,
                'course': True
            },
            {
                'title': 'Office Hours Update',
                'body': 'Office hours this week will be moved to Thursday 3-5pm due to a department meeting.',
                'days_ago': 5,
                'course': True
            }
        ],
        'math_instructor': [
            {
                'title': 'Calculus II Course Overview',
                'body': 'This semester we\'ll cover integration techniques, series, and multivariable calculus. Homework is due weekly on Fridays.',
                'days_ago': 28,
                'course': True
            },
            {
                'title': 'Study Session for Exam',
                'body': 'Optional study session this Saturday 2-4pm in room 301. Bring your questions!',
                'days_ago': 10,
                'course': True
            }
        ],
        'cs_instructor': [
            {
                'title': 'Programming Resources',
                'body': 'Check out the recommended resources page for Python tutorials, documentation, and practice problems.',
                'days_ago': 25,
                'course': True
            },
            {
                'title': 'Project Guidelines Posted',
                'body': 'The final project guidelines and rubric have been posted. Start thinking about your project idea!',
                'days_ago': 12,
                'course': True
            },
            {
                'title': 'Code Review Session',
                'body': 'Bring your code to tomorrow\'s lab session for peer code review. This is a great learning opportunity!',
                'days_ago': 3,
                'course': True
            }
        ],
        'chem_instructor': [
            {
                'title': 'Lab Equipment Checkout',
                'body': 'Lab equipment can be checked out from the stockroom. Please return all equipment by the end of each lab session.',
                'days_ago': 20,
                'course': True
            },
            {
                'title': 'Chemistry Tutoring Available',
                'body': 'Free tutoring is available in the Learning Center Monday-Friday 10am-6pm.',
                'days_ago': 8,
                'course': True
            }
        ],
        'eng_instructor': [
            {
                'title': 'Reading Schedule',
                'body': 'Please stay on top of the reading schedule. Class discussions are much richer when everyone has completed the assigned readings.',
                'days_ago': 18,
                'course': True
            },
            {
                'title': 'Writing Center Hours',
                'body': 'The Writing Center is open for essay consultations. I highly recommend visiting before submitting major papers.',
                'days_ago': 6,
                'course': True
            }
        ]
    }

    # general announcements
    general_announcements = [
        {
            'title': 'Welcome to SpartanSync Demo!',
            'body': 'Welcome to the SpartanSync demo environment! Explore all the features including assignments, grades, messaging, and more. All accounts use password "demo".',
            'days_ago': 35,
            'instructor': 'cs_instructor',
            'course': False
        },
        {
            'title': 'System Maintenance Notice',
            'body': 'SpartanSync will undergo routine maintenance this weekend. The system may be briefly unavailable Saturday night.',
            'days_ago': 14,
            'instructor': 'physics_instructor',
            'course': False
        }
    ]

    announcement_count = 0
    now = datetime.utcnow()

    # course specific announcements
    for instructor_key, templates in announcement_templates.items():
        instructor = instructors[instructor_key]
        course = courses[instructor_key]

        for template in templates:
            created_at = now - timedelta(days=template['days_ago'])

            announcement = Announcement(
                title=template['title'],
                body=template['body'],
                created_at=created_at,
                course_id=course.id,
                created_by=instructor.id
            )
            db.session.add(announcement)
            announcement_count += 1

    # general announcements
    for template in general_announcements:
        created_at = now - timedelta(days=template['days_ago'])
        instructor = instructors[template['instructor']]

        announcement = Announcement(
            title=template['title'],
            body=template['body'],
            created_at=created_at,
            course_id=None,  # General announcement
            created_by=instructor.id
        )
        db.session.add(announcement)
        announcement_count += 1

    db.session.commit()
    print(f"Created {announcement_count} announcements")


def seed_messages(students, instructors, tas):
    print("\nCreating message conversations...")

    conversation_templates = [
        {
            'participants': ['student1', 'physics_instructor'],
            'title': 'Question about Kinematics',
            'messages': [
                {'sender': 'student1', 'body': 'Hi Professor, I have a question about problem 5 on the kinematics problem set. I\'m not sure how to approach the acceleration calculation.', 'days_ago': 7},
                {'sender': 'physics_instructor', 'body': 'Good question! Remember that acceleration is the change in velocity over time. Try breaking down the problem into smaller steps first.', 'days_ago': 7},
                {'sender': 'student1', 'body': 'That makes sense now. Thank you!', 'days_ago': 6}
            ]
        },
        {
            'participants': ['student2', 'cs_ta'],
            'title': 'Help with Data Structures',
            'messages': [
                {'sender': 'student2', 'body': 'Hi, can you explain how linked lists work compared to arrays?', 'days_ago': 5},
                {'sender': 'cs_ta', 'body': 'Sure! Arrays have fixed size and contiguous memory, while linked lists use nodes with pointers. Each has trade-offs in terms of access time and memory.', 'days_ago': 5},
                {'sender': 'student2', 'body': 'Could we go over this in office hours?', 'days_ago': 4},
                {'sender': 'cs_ta', 'body': 'Absolutely! I have office hours tomorrow 2-4pm.', 'days_ago': 4}
            ]
        },
        {
            'participants': ['student3', 'student4'],
            'title': 'Study Group for Chemistry Exam',
            'messages': [
                {'sender': 'student3', 'body': 'Want to form a study group for the stoichiometry exam?', 'days_ago': 9},
                {'sender': 'student4', 'body': 'Yes! How about we meet in the library this weekend?', 'days_ago': 9},
                {'sender': 'student3', 'body': 'Perfect. Saturday at 2pm?', 'days_ago': 8},
                {'sender': 'student4', 'body': 'See you then!', 'days_ago': 8}
            ]
        },
        {
            'participants': ['student5', 'eng_instructor'],
            'title': 'Essay Feedback',
            'messages': [
                {'sender': 'student5', 'body': 'Thank you for the feedback on my literary analysis essay. I appreciate the detailed comments!', 'days_ago': 10},
                {'sender': 'eng_instructor', 'body': 'You\'re welcome! Your analysis of the symbolism was particularly strong. Keep up the good work!', 'days_ago': 10}
            ]
        },
        {
            'participants': ['student1', 'math_instructor'],
            'title': 'Grade Inquiry',
            'messages': [
                {'sender': 'student1', 'body': 'I noticed my grade on the integration techniques homework. Could we discuss where I lost points?', 'days_ago': 12},
                {'sender': 'math_instructor', 'body': 'Of course! Come to office hours and we can go through it together. The main issue was with integration by parts.', 'days_ago': 11}
            ]
        }
    ]

    conversation_count = 0
    message_count = 0
    now = datetime.utcnow()

    all_users = {**students, **instructors, **tas}

    for template in conversation_templates:
        # Get participant users
        participant_users = [all_users[p] for p in template['participants']]

        # Create conversation
        conversation = Conversation(
            title=template['title'],
            is_group=False,
            created_at=now - timedelta(days=template['messages'][0]['days_ago'])
        )
        db.session.add(conversation)
        db.session.flush()

        # Add participants
        for user in participant_users:
            participant = ConversationParticipant(
                conversation_id=conversation.id,
                user_id=user.id,
                last_read_at=now - timedelta(days=random.randint(0, 5))  # Some unread
            )
            db.session.add(participant)

        # Add messages
        for msg_template in template['messages']:
            sender = all_users[msg_template['sender']]
            created_at = now - timedelta(days=msg_template['days_ago'])

            message = Message(
                conversation_id=conversation.id,
                sender_id=sender.id,
                body=msg_template['body'],
                created_at=created_at
            )
            db.session.add(message)
            message_count += 1

        conversation_count += 1

    db.session.commit()
    print(f"Created {conversation_count} conversations with {message_count} messages")


def seed_all(reset=False):
    """Main function to seed all demo data."""
    print("\n" + "="*60)
    print("SpartanSync Demo Data Seeding")
    print("="*60)

    if reset:
        clear_demo_data()

    # Seed users
    users = seed_users()

    # Separate users by role
    students = {k: v for k, v in users.items() if 'student' in k}
    instructors = {k: v for k, v in users.items() if 'instructor' in k}
    tas = {k: v for k, v in users.items() if 'ta' in k}

    # Seed courses
    courses = seed_courses(instructors)

    # Seed assignments with rubrics
    assignments = seed_assignments(courses, instructors)

    # Seed enrollments
    seed_enrollments(students, tas, courses)

    # Seed submissions
    seed_submissions(assignments, students, courses)

    # Seed announcements
    seed_announcements(courses, instructors)

    # Seed messages
    seed_messages(students, instructors, tas)

    print("\n" + "="*60)
    print("Demo data seeding complete!")
    print("="*60)
    print("\nDemo Login Credentials (all passwords: 'demo'):")
    print("\nStudents:")
    print("  - demo-student1 through demo-student5")
    print("\nInstructors:")
    print("  - demo-physics-instructor")
    print("  - demo-math-instructor")
    print("  - demo-cs-instructor")
    print("  - demo-chem-instructor")
    print("  - demo-eng-instructor")
    print("\nTAs:")
    print("  - demo-physics-ta")
    print("  - demo-math-ta")
    print("  - demo-cs-ta")
    print("  - demo-chem-ta")
    print("  - demo-eng-ta")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Seed demo data for SpartanSync')
    parser.add_argument('--reset', action='store_true', help='Clear existing demo data before seeding')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        seed_all(reset=args.reset)
