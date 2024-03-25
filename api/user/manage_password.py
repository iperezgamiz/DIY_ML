import bcrypt
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def hash_password(password):
    """
    Generates a hashed password from a plain text password.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password, encoded in utf-8 for storage.
    """
    try:
        # Generate a salt and hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')  # Return the hashed password as a string for easier storage
    except Exception as e:
        logging.error(f"Error hashing password: {e}")
        raise ValueError("Failed to hash password.") from e


def verify_password(password, hashed_password):
    """
    Verifies a plain text password against a hashed password.

    Args:
        password (str): The plain text password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    try:
        # Ensure both password and hashed_password are bytes for bcrypt
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        # Verify the password against the hashed password
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except Exception as e:
        logging.error(f"Error verifying password: {e}")
        return False
