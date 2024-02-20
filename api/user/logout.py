from flask_restful import Resource, reqparse

class LogoutUser(Resource):

    def get(self, username):

        return {"code": 200, "message": f"User {username} successfully logged out"}
