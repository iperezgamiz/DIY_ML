from flask_restful import Resource
import logging
import json  # Ensure correct import from the standard library


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class OpenUser(Resource):
    def get(self, username):
        """
        Returns a list of model IDs associated with the given username.

        Args:
            username (str): The username of the user whose models are to be fetched.

        Returns:
            A JSON response containing the user's models or an error message.
        """
        try:
            # Retrieve model IDs associated with the user from Redis
            from api.app import redis_db
            user_models_ids_str = redis_db.hget('user:' + username, 'user_models')
            user_models_ids = json.loads(user_models_ids_str) if user_models_ids_str else []

            logging.info(f"Retrieved models for user '{username}'.")
            return {"username": username, "models": user_models_ids}, 200
        except Exception as e:
            logging.error(f"Error retrieving models for user '{username}': {e}")
            # Return a JSON error message with a 500 Internal Server Error status
            return {"error": "An unexpected error occurred while retrieving models."}, 500
