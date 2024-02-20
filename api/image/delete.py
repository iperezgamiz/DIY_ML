from flask_restful import Resource, reqparse

class DeleteImage(Resource):

    def delete(self, project_id, image_id):

        # Find image in database with ID and delete it

        return {"code": 200, "message": f"Image {image_id} successfuly deleted"}


