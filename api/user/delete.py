from flask_restful import Resource, reqparse
from flask import session
from api.user.manage_password import verify_password
import redis

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


user_delete_args = reqparse.RequestParser()
user_delete_args.add_argument("user_password", type=str, required=True)


class DeleteUser(Resource):

    def delete(self, username):

        args = user_delete_args.parse_args()
        user_password = args["user_password"]

        user_db_key = "user:" + username
        stored_password = redis_db.hget(user_db_key, "user_password")
        if verify_password(user_password, stored_password):
            user_email = redis_db.hget(user_db_key, "user_email")
            redis_db.delete(user_db_key)
            redis_db.srem("used_usernames", username)
            redis_db.srem("used_emails", user_email)
            session.pop("username")
            session.pop("last_check")

        return {"code": 200, "message": f"User {username} successfully deleted"}
