from flask_restful import Resource
from flask import session, jsonify
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class LogoutUser(Resource):
    def get(self, username):
        """
        Displays a logout confirmation page.
        """
        return {"message": "Use POST to logout."}, 200

    def post(self, username):
        """
        Logs out the user by clearing their session and recording the logout time.
        """
        try:
            # Clear user session
            session.pop("username", None)  # Safe pop, avoids KeyError if not set
            session.pop("last_check", None)

            # Record logout time in Redis
            from api.app import redis_db
            t = time.strftime('%Y-%m-%d %H:%M:%S')
            redis_db.hset(f"user:{username}", "last_logout", t)

            logging.info(f"User '{username}' logged out successfully at {t}.")
            # Redirecting in an API is not standard; consider returning a success message instead
            return jsonify({"message": f"User '{username}' logged out successfully."}), 200
        except Exception as e:
            logging.error(f"An error occurred during logout for user '{username}': {e}")
            return jsonify({"error": "An unexpected error occurred during logout."}), 500
