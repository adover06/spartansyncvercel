# SpartanSync

A comprehensive Learning Management System built with Flask, featuring role-based access control, assignment management, rubric-based grading, messaging, calendar integration, and AI-powered study planning.

---

## Overview

SpartanSync is a full-featured Learning Management System designed to facilitate communication and collaboration between students, teaching assistants (TAs), and instructors. The platform provides comprehensive tools for managing courses, assignments, submissions, grading, announcements, and more.

**Key Highlights:**
- **Multi-role Support**: Students, TAs, and Instructors with appropriate permissions
- **Course Management**: Create courses, manage enrollments, and organize content
- **Assignment System**: Create assignments with rubric-based grading
- **Messaging**: Direct messaging between users
- **Calendar**: View assignments on a calendar with ICS export
- **AI Study Planner**: OpenAI-powered personalized study plans
- **Weighted Grading**: Automatic grade calculation (Homework 30%, Exam 50%, Project 20%)

---

## Features

### Authentication & Authorization
- Secure login/logout with session management (Flask-Login)
- Role-based access control (Student, TA, Instructor)
- User registration with role selection
- Password hashing with Werkzeug security

### Course Management
- Instructors create and manage courses
- Students enroll in courses via "Manage My Classes"
- Course-specific dashboards and content
- Course codes and descriptions

### Assignment System
- Create assignments with titles, descriptions, due dates, and point values
- Category-based assignments (Homework, Exam, Project)
- Rubric-based grading with multiple criteria
- Assignment status tracking (Published, Closed)
- Allow/disable submissions toggle

### Submissions & Grading
- Students submit assignments with text content
- TAs and Instructors grade submissions using rubrics
- Rubric scores stored in JSON format
- Status tracking (Submitted, Graded)
- Automatic score calculation from rubric criteria

### Announcements
- General and course-specific announcements
- Instructor-only creation and deletion
- Chronological display with course badges
- Filtered by student enrollments

### Messaging
- One-on-one conversations between users
- Conversation threading with message history

### Calendar & Export
- Monthly calendar view of assignments
- Color-coded assignments by course
- ICS export for Google Calendar, Outlook, Apple Calendar
- Export by month or 90-day window

### AI Study Planner
- OpenAI GPT-4 integration for study plan generation
- Personalized recommendations based on assignments
- Considers due dates, point values, and user goals
- Formatted advice with time management tips

### Weighted Grading
- Automatic grade calculation by category
- Configurable weights (Homework 30%, Exam 50%, Project 20%)
- Per-course grade display
- Breakdown by category with earned/possible points

---

## Technology Stack

### Backend
- **Flask**: Python web framework
- **Flask-Login**: User session management
- **Flask-SQLAlchemy**: ORM for database interactions
- **SQLite**: Lightweight database
- **WTForms**: Form validation and rendering

### Frontend
- **Jinja2**: Template engine
- **Tailwind CSS**: Utility-first CSS framework (via CDN)
- **Vanilla JavaScript**: For interactive components

### AI Integration
- **OpenAI API**: GPT-4 mini for study planning

### Testing
- **pytest**: Testing framework
- **pytest fixtures**: Test data management

---

## Installation

### Prerequisites
- Python 3.8+ installed
- Git (for cloning)
- OpenAI API key (optional, for AI Study Planner feature)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SpartanSync
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables** (optional, for AI features):
   - Create a `.env` file in the root directory:
     ```bash
     touch .env
     ```
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```
   - Get an API key from: https://platform.openai.com/api-keys

6. **Initialize the database** (automatic on first run):
   ```bash
   # Optional: Manually create database
   python create_db.py
   ```

---

## Running the Application

### Standard Mode

1. **Activate your virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

2. **Run the application**:
   ```bash
   python run.py
   # or
   flask run --port 5001
   ```

3. **Access the application**:
   Open your browser and navigate to:
   - http://localhost:5001
   - http://127.0.0.1:5001

4. **Create an account**:
   - Visit `/createaccount` or click "Create Account" on the login page
   - Choose your role (Student, TA, or Instructor)
   - Fill in username, email, and password

---

## Demo Mode

SpartanSync includes a comprehensive demo mode with pre-populated data to showcase all features without manual setup.

### Quick Start with Demo Data

1. **Seed the demo data**:
   ```bash
   # Using the seed script
   python seed_demo.py

   # OR using Flask CLI
   flask seed-demo

   # To reset and recreate demo data
   python seed_demo.py --reset
   flask seed-demo --reset
   ```

2. **Start the server**:
   ```bash
   python run.py
   ```

3. **Use Demo Login Buttons**:
   - Visit the login page and click one of the demo buttons:
     - **Student** (blue) - Logs in as demo-student1
     - **Instructor** (purple) - Logs in as demo-cs-instructor
     - **TA** (green) - Logs in as demo-cs-ta

### Demo Accounts

All demo passwords are: `demo`

**Students** (5 total):
- `demo-student1`, `demo-student2`, `demo-student3`, `demo-student4`, `demo-student5`

**Instructors** (5 total):
- `demo-physics-instructor` - Teaches PHYS 101 (Introduction to Physics)
- `demo-math-instructor` - Teaches MATH 201 (Calculus II)
- `demo-cs-instructor` - Teaches CS 101 (Introduction to Programming)
- `demo-chem-instructor` - Teaches CHEM 150 (General Chemistry)
- `demo-eng-instructor` - Teaches ENG 102 (Composition and Literature)

**TAs** (5 total):
- `demo-physics-ta`, `demo-math-ta`, `demo-cs-ta`, `demo-chem-ta`, `demo-eng-ta`
- Each TA assists with their respective subject course

### Demo Data Includes

- **5 Courses**: Physics, Math, CS, Chemistry, English
- **18 Assignments**: 3-4 per course with varied categories (Homework, Exam, Project)
- **Rubric Criteria**: 2-4 criteria per assignment
- **Student Enrollments**: Each student enrolled in 3 courses
- **Submissions**: Mix of graded, submitted, and pending submissions
- **14 Announcements**: Course-specific and general announcements
- **5 Conversations**: Messages between students, instructors, and TAs
- **Varied Due Dates**: Past, current, and upcoming assignments for calendar demo

---

## User Roles

### Student
**Capabilities:**
- View enrolled courses and assignments
- Submit assignments
- View grades and rubric feedback
- Manage class enrollments
- View course announcements
- Send and receive messages
- Use AI Study Planner
- Export calendar to ICS

**Restrictions:**
- Cannot create or delete assignments
- Cannot create announcements
- Cannot grade submissions
- Cannot see other students' submissions

### Teaching Assistant (TA)
**Capabilities:**
- All student capabilities
- Grade submissions for assigned courses
- Add/edit rubric criteria
- View all submissions for assigned courses

**Restrictions:**
- Cannot create or delete assignments
- Cannot create or delete announcements
- Cannot create courses
- Only see courses they're assigned to

### Instructor
**Capabilities:**
- All TA capabilities
- Create and delete courses
- Create and delete assignments
- Create and delete announcements
- Full grading access to all courses they create
- View all student submissions

**Full Control:**
- Complete management of their courses
- Assignment publishing and unpublishing
- Course enrollment visibility

---

## Core Features

### Authentication

**Login** (`/login`):
- Username and password authentication
- "Remember Me" functionality
- Demo login buttons for quick access
- Error messages for invalid credentials

**Registration** (`/createaccount`):
- Username, email, and password required
- Role selection (Student, TA, Instructor)
- Duplicate username/email prevention
- Password hashing with Werkzeug

**Logout** (`/logout`):
- POST-only endpoint
- Session termination
- Redirect to login page

### Dashboard

**Student Dashboard** (`/dashboard`):
- Assignment list filtered by enrolled courses
- Status badges (Pending, Submitted, Graded, Overdue, Closed)
- Submission status per assignment
- Quick links to assignment details
- Recent announcements

**Instructor Dashboard** (`/dashboard`):
- All created assignments
- Pending submissions count
- Quick grading access
- Upcoming assignment overview

**TA Dashboard** (`/dashboard`):
- Assignments from assigned courses
- Submissions needing grading
- Course-filtered content

### Courses

**Create Course** (`/courses/new`) - Instructors only:
- Course name (e.g., "Introduction to Python")
- Course code (unique, e.g., "CS101")
- Description (optional)

**View Courses** (`/courses`):
- Browse all available courses
- Course cards with name, code, description
- Links to course detail pages

**Course Detail** (`/courses/<id>`):
- View course information
- List all course assignments with status
- View course announcements
- Grade information for enrolled students

**Manage Enrollments** (`/classes/manage`) - Students only:
- Multi-select interface
- Choose courses to display on dashboard
- Filter assignments by enrollment
- Saved to Classes table as JSON

### Assignments & Rubrics

**Create Assignment** (`/assignments/new`) - Instructors only:
- Title and description
- Due date and time picker
- Point value (0+)
- Category selection (Homework, Exam, Project)
- Course selection (optional)
- Allow/disable submissions
- Auto-creates default rubric criterion

**View Assignments** (`/assignments`):
- List all assignments (role-filtered)
- Course badges
- Due dates and point values
- Status indicators
- Category tags

**Assignment Detail** (`/assignments/<id>`):
- Full description
- Due date countdown
- Course information
- Points and category
- Rubric criteria display
- Submission form (students)
- Grading interface (instructors/TAs)

**Rubric Management**:
- Add criteria to assignments
- Define title, description, max points
- Flexible point distribution
- Edit/delete criteria (instructors/TAs)

**Delete Assignment** - Instructors only:
- Cascade deletion (removes submissions and rubrics)
- Confirmation required

### Submissions & Grading

**Submit Assignment** (Students):
- Text submission area
- Update before due date
- View submission status
- See graded scores and rubric feedback

**Grade Submissions** (Instructors/TAs):
- View all student submissions
- Rubric-based grading interface
- Score each criterion (0 to max_points)
- Automatic total calculation
- Mark as "Graded"
- Rubric scores stored in JSON

**Submission Status**:
- **Submitted**: Awaiting grading
- **Graded**: Score and feedback available
- **Pending**: Not yet submitted
- **Overdue**: Past due date, not submitted
- **Closed**: Submissions disabled

### Announcements

**Create Announcement** (`/announcements/new`) - Instructors only:
- Title and body
- Course targeting (specific or general)
- Created_at timestamp
- Author tracking

**View Announcements** (`/announcements`):
- List all announcements (course-filtered for students)
- Detail view for each announcement
- Course badges
- Creation date and author
- Chronological ordering

**Delete Announcement** - Instructors only:
- Remove outdated announcements
- Accessible from list/detail views

### Messaging System

**Inbox** (`/messages`):
- List all conversations
- Last message preview
- Sorted by most recent activity
- Participant names

**Create Conversation** (`/messages/new`):
- Select recipient from user list
- Optional conversation title
- Send initial message
- One-to-one conversations

**View Conversation** (`/messages/<id>`):
- Full message thread
- Chronological ordering
- Sender information

**Send Message**:
- Reply to existing conversations
- Multi-message support
- Real-time message display

### Calendar & ICS Export

**Calendar View** (`/calendar`):
- Interactive monthly calendar
- Navigate between months
- Color-coded assignments by course
- Event listings on each day
- Multi-day event support
- Responsive grid layout

**ICS Export** (`/calendar/export`):
- Download assignments as `.ics` file
- Export specific month or 90-day window
- Full iCalendar format (VCALENDAR, VEVENT)
- Compatible with major calendar applications:
  - Google Calendar
  - Outlook
  - Apple Calendar
  - Thunderbird
- Includes assignment title, description, due date
- Respects student enrollments

### AI Study Planner

**Study Plan Generation** (`/study-plan`) - Students only:
- OpenAI GPT-4 mini integration
- Personalized study schedules
- Considers:
  - All unsubmitted assignments
  - Due dates
  - Point values
  - User's topic/area of focus
- Returns formatted advice:
  - Study plan for completing assignments
  - Time management tips
  - Organization strategies
  - References to SpartanSync features
- Error handling if API unavailable

**Usage**:
1. Enter focus area (e.g., "preparing for exams", "managing workload")
2. Click "Generate Study Plan"
3. Receive AI-generated personalized advice

### Weighted Grading

**Grade Calculation**:
- **Category Weights**:
  - Homework: 30%
  - Exam: 50%
  - Project: 20%
- Per-category average calculation
- Percentage conversion (earned/possible)
- Weighted final grade computation
- Handles partial grades

**Display Locations**:
- Course detail pages (enrolled students)
- Home page course cards (enrolled students)
- Dashboard references

**Grade Breakdown**:
- Shows total earned/possible points
- Category-wise breakdown
- Percentage per category
- Final weighted grade

---


### Environment Variables (.env)

```
OPENAI_API_KEY=your-api-key-here
```

---

## Testing

SpartanSync includes comprehensive test coverage using pytest.

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run with coverage report
pytest --cov=app tests/
```

### Test Files

- `test_models.py`: User, Course, Assignment, Submission models
- `test_routes.py`: Core application routes
- `test_forms.py`: Form validation
- `test_messages.py`: Messaging system
- `test_calendar.py`: Calendar and ICS export

### Test Fixtures

Located in `tests/conftest.py`:
- `app`: Flask application with test config
- `client`: Test client for making requests
- `db`: Database instance
- `student_user`, `instructor_user`, `ta_user`: User fixtures
- `course`, `multiple_courses`: Course fixtures
- `assignment`, `multiple_assignments`: Assignment fixtures
- `submission`: Submission fixture
- `announcement`: Announcement fixture
- `rubric_criterion`: Rubric fixture

---

## API Integration

### OpenAI API (Study Planner)

**File**: `app/main/gpt_client.py`

**Function**: `generate_study_plan(prompt: str) -> str`
- Uses GPT-4 mini model
- Constructs prompt from assignment data
- Returns formatted study advice

---

## Troubleshooting

### Database Issues

**Problem**: Database not created
```bash
# Solution: Manually create database
python create_db.py
```

**Problem**: Database locked error
```bash
# Solution: Close all connections and restart server
# Kill any running Flask processes
pkill -f flask
# Restart server
python run.py
```

### Port Issues

**Problem**: Port already in use
```bash
# Solution: Use a different port
flask run --port 5002
# OR
python run.py  # Configured for port 5001
```

### Virtual Environment Issues

**Problem**: ModuleNotFoundError
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Demo Data Issues

**Problem**: Demo users already exist
```bash
# Solution: Reset demo data
python seed_demo.py --reset
# OR
flask seed-demo --reset
```

### OpenAI API Issues

**Problem**: Study planner not working
```bash
# Check if .env file exists with API key
cat .env

# Verify API key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

---


### Adding New Features

1. **Create database model** in `app/models.py`
2. **Create form** in `app/forms.py`
3. **Add route** in appropriate blueprint (`app/auth/routes.py` or `app/main/routes.py`)
4. **Create template** in `app/templates/` or blueprint templates
5. **Add tests** in `tests/`
6. **Update demo data** in `seed_demo.py` if needed

### Database Migrations

Currently using SQLite with manual schema updates. To modify database:

1. Edit models in `app/models.py`
2. Delete `app/app.db`
3. Run `python create_db.py`
4. Reseed demo data: `python seed_demo.py`

---

## Quick Reference

### URLs
- Login: `/login`
- Dashboard: `/dashboard`
- Home: `/home`
- Courses: `/courses`
- Assignments: `/assignments`
- Announcements: `/announcements`
- Messages: `/messages`
- Calendar: `/calendar`
- Study Plan: `/study-plan` (students)
- Manage Classes: `/classes/manage` (students)

### Flask CLI Commands
```bash
flask run                  # Start development server
flask seed-demo            # Seed demo data
flask seed-demo --reset    # Reset and reseed demo data
```

### Demo Quick Start
```bash
python seed_demo.py        # Seed demo data
python run.py              # Start server
# Visit http://localhost:5001/login
# Click "Student", "Instructor", or "TA" button
```

