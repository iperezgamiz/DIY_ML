from flask_restful import Resource, reqparse

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
        # If the username and password match, return succesful statement

        return {"code": 200, "message": f"User {username} successfully logged in"}
