""" This is a module that generate the hash password and then vaildate password """
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(password):
    """Generate a hashed password."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Check if a password matches its hashed version."""
    return check_password_hash(hashed_password, password)
