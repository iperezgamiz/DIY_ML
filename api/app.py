import redis
from flask import Flask
from flask_restful import Api, Resource
from user.create import CreateUser
from user.login import LoginUser
from user.open import OpenUser
from user.logout import LogoutUser
from user.delete import DeleteUser
from model.create import CreateModel
from model.open import OpenModel
from model.trainModel import TrainModel
from model.trainReport import TrainReport
from model.testModel import TestModel
from model.testReport import TestReport
from model.deployModel import DeployModel
from model.inference import InferImage
from queues.training_queue import start_training_thread

app = Flask(__name__)
api = Api(app)
app.secret_key = 'secret_key'

# Connect to Redis
redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class Home(Resource):
    def get(self):
        return {"message": "home page"}, 200


api.add_resource(Home, '/')
api.add_resource(CreateUser, '/user/signup')
api.add_resource(LoginUser, '/user/login')
api.add_resource(OpenUser, '/user/<string:username>')
api.add_resource(LogoutUser, '/user/<string:username>/logout')
api.add_resource(DeleteUser, '/user/<string:username>/delete')
api.add_resource(CreateModel, '/model/create')
api.add_resource(OpenModel, '/model/<string:model_id>')
api.add_resource(TrainModel, '/model/<string:model_id>/trainModel')
api.add_resource(TrainReport, '/model/<string:model_id>/trainReport')
api.add_resource(TestModel, '/model/<string:model_id>/testModel')
api.add_resource(TestReport, '/model/<string:model_id>/testReport')
api.add_resource(DeployModel, '/model/<string:model_id>/deployModel')
api.add_resource(InferImage, '/model/<string:model_id>/inferImage')

if __name__ == "__main__":
    start_training_thread()
    app.run(debug=True)
