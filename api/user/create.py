from flask_restful import Resource, reqparse
import uuid

user_create_args = reqparse.RequestParser()
user_create_args.add_argument("user_email", type=str, required=True)
user_create_args.add_argument("username", type=str, required=True)
user_create_args.add_argument("user_password", type=str, required=True)

class CreateUser(Resource):

    def post(self):
        # Generate user ID
        user_id = str(uuid.uuid4())

        # Get user email and password
        args = user_create_args.parse_args()
        user_email = args["user_email"]
        username = args["username"]
        user_password = args["user_password"]

        # Create json object to save in database
        user_data = {"user_id": user_id, "user_email": user_email, "username": username, "user_password": user_password}
        # Check if the user already exists to avoid repetition

        return {"code": 200, "message": f"User {username} successfully created"}