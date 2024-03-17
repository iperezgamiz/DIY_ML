from flask import Flask, render_template
from flask_restful import Api, Resource
from user.create import CreateUser
from user.login import LoginUser
from user.logout import LogoutUser
from user.delete import DeleteUser
from model.create import CreateModel
from model.open import OpenModel
from model.delete import DeleteModel
from model.uploadImages import UploadImages
from model.trainModel import TrainModel

app = Flask(__name__)
api = Api(app)
app.secret_key = "secret_key"


class Home(Resource):
    def get(self):
        return {"message": "home page"}


api.add_resource(Home, '/')
api.add_resource(CreateUser, '/user/signup')
api.add_resource(LoginUser, '/user/login')
api.add_resource(LogoutUser, '/user/<string:username>/logout')
api.add_resource(DeleteUser, '/user/<string:username>/delete')
api.add_resource(CreateModel, '/model/create')
api.add_resource(OpenModel, '/model/open')
api.add_resource(DeleteModel, '/model/<string:model_id>/delete')
api.add_resource(UploadImages, '/model/<string:model_id>/uploadImages')
api.add_resource(TrainModel, '/model/<string:model_id>/trainModel')


@app.route('/model/<string:model_id>/uploadImages')
def upload_images_form(model_id):
    # Render the upload form template
    return render_template('upload_image.html', model_id=model_id)


@app.route('/model/<string:model_id>/trainModel')
def train_model_form(model_id):
    return render_template('train_model.html')


if __name__ == "__main__":
    app.run(debug=True)
