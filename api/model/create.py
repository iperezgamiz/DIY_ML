from flask_restful import Resource, reqparse
import uuid
import json
import logging


# Configure argument parser for model creation
model_create_args = reqparse.RequestParser()
model_create_args.add_argument("model_name", type=str, required=True, location='form')
model_create_args.add_argument("owner_username", type=str, required=True, location='json')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class CreateModel(Resource):
    def post(self):
        """
        Creates a new model with a unique ID and the specified name,
        associating it with the owner's username.
        """
        try:
            # Parse arguments from the request
            args = model_create_args.parse_args()
            model_name = args["model_name"]
            owner_username = args["owner_username"]  # Now expected in the request body

            # Generate a unique model ID
            model_id = str(uuid.uuid4())

            # Prepare model data for storage
            model_data = {
                "owner_username": owner_username,
                "model_id": model_id,
                "model_name": model_name,
                "trained": "False",
                "deployed": "False"
            }

            # Store model data in Redis
            from api.app import redis_db
            model_db_key = f"model:{model_id}"
            redis_db.hmset(model_db_key, model_data)

            # Update the owner's list of models
            user_models_str = redis_db.hget(f"user:{owner_username}", "user_models")
            user_models = json.loads(user_models_str) if user_models_str else []
            user_models.append(model_id)
            redis_db.hset(f"user:{owner_username}", "user_models", json.dumps(user_models))

            logging.info(f"Model '{model_name}' with ID '{model_id}' created successfully for user '{owner_username}'.")

            # Return a success message with the model ID
            return {
                "message": "Model created successfully.",
                "model_id": model_id
            }, 201  # HTTP status code for Created
        except Exception as e:
            logging.error(f"Error creating model: {e}")
            return {"error": "Failed to create model due to an internal error."}, 500
