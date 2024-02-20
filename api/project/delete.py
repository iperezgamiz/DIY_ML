from flask_restful import Resource, reqparse

project_delete_args = reqparse.RequestParser()
project_delete_args.add_argument("user_password", type=str, required = True)

class DeleteProject(Resource):

    def delete(self, project_id):

        args = project_delete_args.parse_args()
        user_password = args["user_password"]

        # Find project in database with ID
        # If user key matches the introduced key, delete project

        return {"message": f"Project {project_id} successfuly deleted"}, 201


