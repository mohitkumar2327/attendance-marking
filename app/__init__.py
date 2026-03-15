from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db    = SQLAlchemy()
mail  = Mail()
login = LoginManager()
login.login_view = "auth.login"

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login.init_app(app)

    from .routes.auth       import auth_bp
    from .routes.admin      import admin_bp
    from .routes.student    import student_bp
    from .routes.attendance import attendance_bp
    from .routes.reports    import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()
        _create_default_admin()

    return app

def _create_default_admin():
    from .models import Admin
    from werkzeug.security import generate_password_hash
    if not Admin.query.first():
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created → username: admin  password: admin123")