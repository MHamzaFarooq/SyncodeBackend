import bcrypt

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'),salt)

def verify_password(provided_password, stored_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(provided_password.encode('utf-8'),stored_password.encode('utf-8'))