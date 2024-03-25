from flask_restful import Resource
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class OpenModel(Resource):
    def get(self, model_id):
        """
        Returns model data if the model is trained. Otherwise, it advises training the model.

        Args:
            model_id (str): The ID of the model to be opened.

        Returns:
            A JSON object containing the model's data or a message indicating the model needs training.
        """
        try:
            from api.app import redis_db
            trained = redis_db.hget(f"model:{model_id}", "trained")

            if trained == "True":
                model_data = redis_db.hgetall(f"model:{model_id}")
                logging.info(f"Accessed data for model '{model_id}'.")
                return model_data, 200
            else:
                logging.info(f"Model '{model_id}' is not trained. Advising to train the model.")
                # Instead of redirecting, return a JSON response indicating the next action
                return {
                    "message": "Model is not trained. Please train the model first.",
                    "action_required": "train",
                    "train_model_url": f"/model/{model_id}/trainModel"  # Providing URL for client-side action
                }, 400  # Using 400 Bad Request to indicate further action is needed
        except Exception as e:
            logging.error(f"Error retrieving model '{model_id}': {e}")
            return {"error": "Failed to retrieve model data due to an internal error."}, 500
