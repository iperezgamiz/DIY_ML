from flask_restful import Resource, reqparse

project_open_args = reqparse.RequestParser()
project_open_args.add_argument("project_id", type=str, required=True)

class OpenProject(Resource):

    def get(self):

        args = project_open_args.parse_args()
        project_id = args["project_id"]

        # Get project data from database to return

        return {"code": 20, "message": f"Project {project_id} successfully opened"} 