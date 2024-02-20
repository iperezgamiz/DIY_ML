from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
import uuid

image_post_args = reqparse.RequestParser()
image_post_args.add_argument("image_file", type=FileStorage, location='files', required=True)
image_post_args.add_argument("image_label", type=FileStorage, location='files', required=True)


class UploadImage(Resource):

    def post(self, project_id):
        # Generate image ID
        image_id = str(uuid.uuid4())

        # Get image file
        args = image_post_args.parse_args()
        image_file = args["image_file"]
        image_label = args["image_label"]

        # Create json object and save in database
        image_data = {"image_id": image_id, "image_file": image_file, "image_label": image_label}

        return {"code": 201, "message": f"Image {image_id} with label {image_label} successfully uploaded"}
