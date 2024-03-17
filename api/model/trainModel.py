import json
import pickle
import zipfile

from flask_restful import Resource, reqparse
from mega import Mega
import redis
import tempfile
import os
from api.train.cnn import CnnModel

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

trainModel_args = reqparse.RequestParser()
trainModel_args.add_argument('image_size_0', type=int, required=True)
trainModel_args.add_argument('image_size_1', type=int, required=True)
trainModel_args.add_argument('batch_size', type=int, required=True)
trainModel_args.add_argument('epochs', type=int, required=True)
trainModel_args.add_argument('validation_split', type=float, required=True)

# MEGA access credentials
EMAIL = 'ec530storage@gmail.com'
PASSWORD = 'Txuleton99'

# Log in to MEGA
mega = Mega()
m = mega.login(EMAIL, PASSWORD)


class TrainModel(Resource):

    def post(self, model_id):

        args = trainModel_args.parse_args()
        image_size_0 = args['image_size_0']
        image_size_1 = args['image_size_1']
        image_size = (image_size_0, image_size_1)
        batch_size = args['batch_size']
        epochs = args['epochs']
        validation_split = args['validation_split']

        mega_folder_name = redis_db.hget("model:"+model_id, "dataset_location")
        dataset_name = redis_db.hget("model:"+model_id, "dataset_name")
        dataset = m.find(dataset_name, mega_folder_name)

        if dataset:
            # Get a temporary directory to store the file
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, dataset_name)

            # Download the file to the temporary directory
            m.download(dataset, temp_file_path)
        else:
            return {"code": 400, "message": "Dataset not found"}

        # Unzip file
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            # Extract all contents to the specified directory
            zip_ref.extractall(temp_dir)

        unzipped_dataset_path = os.path.join(temp_dir, dataset_name[:-4])
        cnn = CnnModel(model_id, unzipped_dataset_path, image_size, batch_size, epochs, validation_split)
        results_temp_path = cnn.run()

        # Update database
        redis_db.hset("model:"+model_id, "trained", str(True))
        model_bytes = pickle.dumps(os.path.join(results_temp_path, f"{model_id}.h5"))
        redis_db.hset("model:"+model_id, "model_file", model_bytes)
        with open(os.path.join(results_temp_path, "class_labels.txt"), 'r') as class_labels:
            class_labels_content = class_labels.read()
        redis_db.hset("model:"+model_id, "class_labels", class_labels_content)
        report_data = json.dumps(os.path.join(results_temp_path, "report_data.json"))
        redis_db.hset("model:"+model_id, "report_data", report_data)
        with open(os.path.join(results_temp_path, "accuracy_plot.png"), 'r') as accuracy_plot:
            acc_plot_data = accuracy_plot.read()
        redis_db.hset("model:"+model_id, "accuracy_plot", acc_plot_data)
        with open(os.path.join(results_temp_path, "loss_plot.png"), 'r') as loss_plot:
            loss_plot_data = loss_plot.read()
        redis_db.hset("model:"+model_id, "loss_plot", loss_plot_data)
        training_params = {"image_size": image_size, "batch_size": batch_size, "epochs": epochs,
                           "validation_split": validation_split}
        redis_db.hset("model:"+model_id, "training_params", training_params)

        # Delete temporary directory for results
        os.remove(temp_dir)
        os.remove(results_temp_path)

        return {"code": 200, "message": "Model successfully trained"}






