from flask_restful import Resource
from flask import session
import redis
import time

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class LogoutUser(Resource):

    def post(self, username):

        session.pop("username")
        session.pop("last_check")
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        redis_db.hset("user:" + username, "last_logout", t)

        return {"code": 200, "message": f"User {username} successfully logged out"}
