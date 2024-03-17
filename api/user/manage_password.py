import bcrypt


def hash_password(password):
    # Generate a salt and hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password


def verify_password(password, hashed_password):
    # Ensure both password and hashed_password are bytes
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # Verify the password against the hashed password
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)
