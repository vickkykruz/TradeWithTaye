"""
This is the module that holds the call of the database
"""
from flask_sqlalchemy import SQLAlchemy
import logging

db = SQLAlchemy()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
