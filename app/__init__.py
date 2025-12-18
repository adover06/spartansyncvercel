from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import click
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    _ensure_sqlite_database(app)

    # Register CLI commands
    register_cli_commands(app)

    return app


def register_cli_commands(app):
    @app.cli.command('seed-demo')
    @click.option('--reset', is_flag=True, help='Clear existing demo data before seeding')
    def seed_demo_command(reset):
        """Seed the database with demo data for testing and demonstrations."""
        from seed_demo import seed_all
        seed_all(reset=reset)


def _ensure_sqlite_database(app):
    """Create SQLite DB (if missing) the first time the app boots."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not uri.startswith("sqlite"):
        return

    # Extract filesystem path from sqlite:/// URI
    db_path = uri.replace("sqlite:///", "", 1)
    if not os.path.isabs(db_path):
        db_path = os.path.join(app.root_path, db_path)

    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with app.app_context():
            db.create_all()


