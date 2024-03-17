from flask_restful import Resource, reqparse
from flask import session
import redis
import json

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class DeleteModel(Resource):

    def delete(self, model_id):

        model_owner = redis_db.hget("model:" + model_id, "owner_username")
        if session["username"] == model_owner:
            trained = redis_db.hget("model:" + model_id, "trained")
            if trained == "True":
                report_id = redis_db.hget("model:"+model_id, "report_id")
                user_reports = set(json.loads(redis_db.hget("user:" + session["username"], "user_reports")))
                user_reports.remove(report_id)
                user_reports = list(user_reports)
                redis_db.hset("user:" + session["username"], "user_reports", json.dumps(user_reports))
                redis_db.delete("report:"+report_id)
            redis_db.delete("model:" + model_id)
            user_models = set(json.loads(redis_db.hget("user:" + session["username"], "user_models")))
            user_models.remove(model_id)
            user_models = list(user_models)
            redis_db.hset("user:" + session["username"], "user_models", json.dumps(user_models))

            return {"code": 201, "message": f"Model {model_id} successfully deleted"}
