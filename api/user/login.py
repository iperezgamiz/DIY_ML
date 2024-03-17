from flask_restful import Resource, reqparse
from flask import session
import redis
import time
from api.user.manage_password import verify_password

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

user_login_args = reqparse.RequestParser()
user_login_args.add_argument("username", type=str, required=True)
user_login_args.add_argument("user_password", type=str, required=True)


class LoginUser(Resource):

    def get(self):
        # Get user email and password
        args = user_login_args.parse_args()
        username = args["username"]
        user_password = args["user_password"]

        # Find user in database
        user_db_key = "user:" + username
        if redis_db.exists(user_db_key):
            stored_password = redis_db.hget(user_db_key, "user_password")
            if verify_password(user_password, stored_password):
                t = time.strftime('%Y-%m-%d %H:%M:%S')
                redis_db.hset("user:"+username, "last_login", t)
                session["username"] = username
                session["last_check"] = t
                return {"code": 200, "message": f"User {username} successfully logged in"}

        return {"code": 401, "message": "Invalid email or password"}
