from flask_restful import Resource
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


class DeployModel(Resource):
    def post(self, model_id):
        try:
            # Set the deployed status of the model in Redis
            from api.app import redis_db
            redis_db.hset("model:" + model_id, "deployed", str(True))
            logging.info(f"Model {model_id} successfully deployed")
            return {"message": "model successfully deployed"}
        except Exception as e:
            # Log an error message if an exception occurs
            logging.error(f"Failed to deploy model {model_id}: {e}")
            return {"message": "failed to deploy model"}, 500
