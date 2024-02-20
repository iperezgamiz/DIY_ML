from flask_restful import Resource, reqparse
import uuid

project_create_args = reqparse.RequestParser()
project_create_args.add_argument("project_name", type=str, required=True)

class CreateProject(Resource):

    def post(self):
        # Generate project ID
        project_id = str(uuid.uuid4())

        # Get project name
        args = project_create_args.parse_args()
        project_name = args["project_name"]

        # Create json object and save in database
        project_data = {"project_id": project_id, "project_name": project_name}

        return {"code": 201, "message": f"Project {project_name} successfully created"}
