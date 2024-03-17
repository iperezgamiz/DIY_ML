from flask_restful import Resource, reqparse
import redis
import json
from api.user.manage_password import hash_password

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

user_create_args = reqparse.RequestParser()
user_create_args.add_argument("user_email", type=str, required=True)
user_create_args.add_argument("username", type=str, required=True)
user_create_args.add_argument("user_password", type=str, required=True)


class CreateUser(Resource):

    def post(self):
        # Get user email and password
        args = user_create_args.parse_args()
        user_email = args["user_email"]
        username = args["username"]
        user_password = args["user_password"]

        if redis_db.sismember("used_emails", user_email):
            return {"code": 400, "message": "There is already an account registered with this email"}
        elif redis_db.sismember("used_usernames", username):
            return {"code": 400, "message": "The username is not available"}
        else:
            redis_db.sadd("used_usernames", username)
            redis_db.sadd("used_emails", user_email)

        user_db_key = "user:" + username
        hashed_user_password = hash_password(user_password)
        user_data = {"user_email": user_email, "user_name": username, "user_password": hashed_user_password,
                     "user_models": json.dumps(list()), "user_reports": json.dumps(list()), "last_login": "",
                     "last_logout": ""}

        # Check if the user already exists to avoid repetition

        if redis_db.exists(user_db_key):
            return {"code": 400, "message": "User already exists"}

        # Save user data in Redis
        redis_db.hmset(user_db_key, user_data)

        return {"code": 200, "message": f"User {username} successfully created"}
