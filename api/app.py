from flask import Flask
from flask_restful import Api, Resource
from user.create import CreateUser
from user.login import LoginUser
from user.logout import LogoutUser
from user.delete import DeleteUser
from project.create import CreateProject
from project.open import OpenProject
from project.delete import DeleteProject
from image.upload import UploadImage
from image.delete import DeleteImage

app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
        return {"message": "home page"}

api.add_resource(Home, '/')
api.add_resource(CreateUser, '/user/signup')
api.add_resource(LoginUser, '/user/login')
api.add_resource(LogoutUser, '/user/<string:username>')
api.add_resource(DeleteUser, '/user/<string:username>')
api.add_resource(CreateProject, '/project/create')
api.add_resource(OpenProject, '/project')
api.add_resource(DeleteProject, '/project/<string:project_id>')
api.add_resource(UploadImage, '/project/<string:project_id>/image')
api.add_resource(DeleteImage, '/project/<string:project_id>/image/<string:image_id>')





if __name__ == "__main__":
    app.run(debug=True)