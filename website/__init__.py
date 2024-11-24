import os
import secrets
from flask import Flask, render_template, send_from_directory, current_app
from jinja2 import FileSystemLoader
from website.database.database import db
from website.mailer.mail import mail
from website.clients.models.views import views
from website.clients.models.users import shuffle_list
from website.clients.models.auth import auth
from website.admin.models.auth import adminAuth
from website.admin.models.views import adminViews
from os import path, environ
from datetime import timedelta
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from website.admin.models.models import Admin
import logging
from logging.handlers import RotatingFileHandler

# Connect to database
DB_NAME = 'trade_with_taye_oj.db'

# Here to store the uploaded images
UPLOAD_FOLDER = 'website/static/uploads'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    """ This is a function that issues the name of the app """
    app = Flask(__name__) # This represent the name of the file

    # Configure logging
    if not app.debug:
        file_handler = RotatingFileHandler('flask.log', maxBytes=10240, backupCount=1)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # This is going to encrpt or secure D cookie
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'fallback_secret_key')
    # Set session timeout to 1 hour (for example)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are only sent over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Helps mitigate cross-site scripting (XSS)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Define template folders for clients and admin
    client_template_folder = path.join(app.root_path, 'clients', 'templates')
    admin_template_folder = path.join(app.root_path, 'admin', 'templates')

    # Configure Jinja2 environment with multiple template folders
    loader = FileSystemLoader([client_template_folder, admin_template_folder])
    app.jinja_loader = loader  # Set the Jinja loader directly to the Flask app

    # Connect to our database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'mail.joamcollections.com.ng'  # Your email server (e.g., smtp.gmail.com)
    app.config['MAIL_PORT'] = 587  # Port for your email server (e.g., 587 for Gmail)
    app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
    app.config['MAIL_USERNAME'] = 'info@joamcollections.com.ng'  # Your email address
    app.config['MAIL_PASSWORD'] = 'Joam_collections'  # Your email password

    db.init_app(app)
    mail.init_app(app)

    # Register the blueprint
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(adminAuth, url_prefix='/admin')
    app.register_blueprint(adminViews, url_prefix='/admin/page')

    # Register the shuffle function as a filter
    app.jinja_env.filters['shuffle'] = shuffle_list

    # Custom error handler for 404 Not Found
    @app.errorhandler(404)
    def page_not_found(error):
        """ This is a function that handle the 404 error handlers """
        return render_template('404.html')


    @app.errorhandler(500)
    def internal_server_error(error):
        """ This is a function that handler the 500 error handlers """
        return render_template('500.html')


    @app.errorhandler(405)
    def method_not_found(error):
        """ This is a function that handler the 405 error handlers """
        return render_template('405.html')


    # @app.before_request
    # def log_request_info():
    #    app.logger.info('Headers: %s', request.headers)
    #    app.logger.info('Body: %s', request.get_data())


    # Define the route for serving uploaded files
    @app.route('/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    # Import the schemer of our database
    from website.clients.models.models import User
    from website.admin.models.models import Admin
    # create_database(app)
    if create_database(app):
        with app.app_context():
            create_default_admin()

    # Return the app
    return app

def create_database(app):
    """ This is a function that create the database """

    db_path = path.join('instance', DB_NAME)

    # check if the path of our database doesn't exist then create it
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
        print('Created Database')
        return True
    return False


def create_default_admin():
    """ This is a function that insert that admin records """
    # Check if the default record already exists
    if not Admin.query.filter_by(username='VickkyKruz').first():
        admin = Admin(
            username='VickkyKruz',
            email='onwuegbuchulemvic02@gmail.com',
            password_hash=generate_password_hash('password123'),
            working_status='working',
            admin_office='super_admin'
        )
        db.session.add(admin)
        db.session.commit()
