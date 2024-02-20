from flask_restful import Resource, reqparse

user_delete_args = reqparse.RequestParser()
user_delete_args.add_argument("user_password", type=str, required = True)

class DeleteUser(Resource):

    def delete(self, username):

        args = user_delete_args.parse_args()
        user_password = args["user_password"]

        # Find user in database with username
        # If user password matches the introduced password, delete user

        return {"code": 200, "message": f"User {username} successfully deleted"}