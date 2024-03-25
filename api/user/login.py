from flask_restful import Resource, reqparse
import time
from flask import url_for
from api.user.manage_password import verify_password
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# Set up argument parser for login functionality
user_login_args = reqparse.RequestParser()
user_login_args.add_argument("username", type=str, required=True, location='form')
user_login_args.add_argument("user_password", type=str, required=True, location='form')


class LoginUser(Resource):
    def get(self):
        """
        Inform the client that this endpoint expects a POST request with username and user_password.
        """
        return {"message": "Please use a POST request to log in with 'username' and 'user_password'."}, 200

    def post(self):
        """
        Authenticates a user based on username and password.

        On successful authentication, returns a message indicating login success,
        a redirect URL, and the last login timestamp.
        """
        try:
            args = user_login_args.parse_args()
            username = args["username"]
            user_password = args["user_password"]

            from api.app import redis_db
            user_db_key = "user:" + username
            if redis_db.exists(user_db_key):
                stored_password = redis_db.hget(user_db_key, "user_password")
                if verify_password(user_password, stored_password):
                    t = time.strftime('%Y-%m-%d %H:%M:%S')
                    redis_db.hset(user_db_key, "last_login", t)
                    logging.info(f"User '{username}' logged in successfully.")

                    redirect_url = url_for('openuser', username=username, _external=True)
                    return {
                        "message": "Login successful.",
                        "redirect_url": redirect_url,
                        "last_login": t
                    }, 200

            logging.warning(f"Login failed for user: {username}")
            return {"message": "Invalid username or password"}, 401

        except Exception as e:
            logging.error(f"An error occurred during login attempt: {e}")
            return {"message": "An unexpected error occurred during login attempt."}, 500
