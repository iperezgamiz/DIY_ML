from flask import url_for
from flask_restful import Resource, reqparse
import json
import logging
from .manage_password import hash_password

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# Define argument parser for user creation
user_create_args = reqparse.RequestParser()
user_create_args.add_argument("user_email", type=str, required=True, location='form')
user_create_args.add_argument("username", type=str, required=True, location='form')
user_create_args.add_argument("user_password", type=str, required=True, location='form')

class CreateUser(Resource):
    def get(self):
        """
        Responds with a message and required parameters for signing up a user.
        """
        return {"message": "Signup user interface",
                "required parameters": ["user_email", "username", "user_password"]}, 200

    def post(self):
        """
        Attempts to create a new user account with the provided username, email, and password.
        Handles potential errors gracefully.
        """
        try:
            args = user_create_args.parse_args()
            user_email = args["user_email"]
            username = args["username"]
            user_password = args["user_password"]

            from api.app import redis_db
            # Check if email or username is already used
            if redis_db.sismember("used_emails", user_email):
                return {"message": "There is already an account registered with this email"}, 400
            elif redis_db.sismember("used_usernames", username):
                return {"message": "The username is not available"}, 400

            # Add username and email to their respective sets
            redis_db.sadd("used_usernames", username)
            redis_db.sadd("used_emails", user_email)

            user_db_key = "user:" + username
            hashed_user_password = hash_password(user_password)
            user_data = {
                "user_email": user_email,
                "user_name": username,
                "user_password": hashed_user_password,
                "user_models": json.dumps([]),
                "last_login": "",
                "last_logout": ""
            }

            if redis_db.exists(user_db_key):
                # Avoid creating duplicate user entries
                return {"message": "User already exists"}, 400

            # Persist user data into Redis
            redis_db.hmset(user_db_key, user_data)
            logging.info(f"User {username} created successfully.")

            # Return success message with login URL
            login_url = url_for('loginuser', _external=True)  # Using _external=True to generate an absolute URL
            return {
                "message": "User created successfully. Please login.",
                "login_url": login_url
            }, 201  # HTTP status code for Created
        except Exception as e:
            logging.error(f"Failed to create user {username}: {e}")
            return {"error": "An unexpected error occurred. Please try again later."}, 500
