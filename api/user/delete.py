from flask_restful import Resource, reqparse
from api.user.manage_password import verify_password
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Set up argument parser for deleting user accounts
user_delete_args = reqparse.RequestParser()
user_delete_args.add_argument("user_password", type=str, required=True, location='form')


class DeleteUser(Resource):
    def post(self, username):
        """
        Attempts to delete a user account after verifying the provided password.
        """
        try:
            args = user_delete_args.parse_args()
            user_password = args["user_password"]

            from api.app import redis_db
            user_db_key = f"user:{username}"
            stored_password = redis_db.hget(user_db_key, "user_password")

            if verify_password(user_password, stored_password):
                self._delete_user_account(username, user_db_key)
                logging.info(f"User account '{username}' deleted successfully.")
                return {"message": f"User account '{username}' deleted successfully."}, 200
            else:
                logging.warning(f"Attempted deletion of user '{username}' with incorrect password.")
                return {"message": "Incorrect password, account deletion failed."}, 401
        except Exception as e:
            logging.error(f"Error during account deletion for user '{username}': {e}")
            return {"error": "An unexpected error occurred. Please try again later."}, 500

    def _delete_user_account(self, username, user_db_key):
        """
        Deletes the user account and associated data from Redis, handling exceptions gracefully.
        """
        try:
            user_email = redis_db.hget(user_db_key, "user_email")
            user_models_ids_str = redis_db.hget(user_db_key, 'user_models')
            user_models_ids = [] if not user_models_ids_str else user_models_ids_str.split(',')

            for user_model_id in user_models_ids:
                redis_db.delete(f"model:{user_model_id}")

            redis_db.delete(user_db_key)
            redis_db.srem("used_usernames", username)
            redis_db.srem("used_emails", user_email)
        except Exception as e:
            logging.error(f"Error deleting data for user '{username}': {e}")
            # Raising exception to be caught in the post method for a unified error response
            raise
