from flask_restful import Resource, reqparse
import redis

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

model_open_args = reqparse.RequestParser()
model_open_args.add_argument("model_id", type=str, required=True)


class OpenModel(Resource):

    def get(self):

        args = model_open_args.parse_args()
        model_id = args["model_id"]

        # Get model data from database to return
        model_data = redis_db.hgetall("model:"+model_id)

        return {"code": 200, "model_data": model_data}
