from flask_restful import Resource, reqparse
from flask import session
import uuid
import redis
import json

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

model_create_args = reqparse.RequestParser()
model_create_args.add_argument("model_name", type=str, required=True)


class CreateModel(Resource):

    def post(self):
        # Generate model ID
        model_id = str(uuid.uuid4())

        args = model_create_args.parse_args()
        model_name = args["model_name"]

        model_data = {"owner_username": session["username"], "model_id": model_id, "model_name": model_name,
                      "trained": str(False)}

        model_db_key = "model:" + model_id
        redis_db.hmset(model_db_key, model_data)

        user_models = set(json.loads(redis_db.hget("user:" + session["username"], "user_models")))
        user_models.add(model_id)
        user_models = list(user_models)
        redis_db.hset("user:" + session["username"], "user_models", json.dumps(user_models))

        return {"code": 201, "message": f"Model {model_name} successfully created"}
