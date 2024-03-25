import json
import zipfile
import shutil
import tempfile
import os
import logging

from flask import session
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from mega import Mega
from queues.training_queue import training_queue

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Define argument parser for model training
trainModel_args = reqparse.RequestParser()
trainModel_args.add_argument('dataset_file', location='files', type=FileStorage, required=True)
trainModel_args.add_argument('image_size_1', type=int, required=True, location='form')
trainModel_args.add_argument('image_size_2', type=int, required=True, location='form')
trainModel_args.add_argument('batch_size', type=int, required=True, location='form')
trainModel_args.add_argument('epochs', type=int, required=True, location='form')
trainModel_args.add_argument('validation_split', type=float, required=True, location='form')

# MEGA access credentials
EMAIL = 'your_email@gmail.com'
PASSWORD = 'your_password'

# Log in to MEGA
mega = Mega()
m = mega.login(EMAIL, PASSWORD)

class TrainModel(Resource):

    def get(self, model_id):
        return {"message": "Please submit a POST request to train a model."}, 200

    def post(self, model_id):
        """
        Queues a model training request with specified parameters.
        """
        try:
            args = trainModel_args.parse_args()
            file_storage = args['dataset_file']
            image_size = (args['image_size_1'], args['image_size_2'])
            batch_size = args['batch_size']
            epochs = args['epochs']
            validation_split = args['validation_split']

            # Process the dataset file and prepare training parameters
            temp_dir, temp_file_path = self._save_dataset_temporarily(file_storage)
            self._queue_training_request(model_id, temp_dir, temp_file_path, file_storage.filename,
                                         image_size, batch_size, epochs, validation_split)

            logging.info(f"Model training for {model_id} queued successfully.")
            # Redirect to a status page or return success message
            return {"message": "Model training initiated. Please check the training status."}, 202
        except Exception as e:
            logging.error(f"Error in queuing model training for {model_id}: {e}")
            return {"error": "Failed to queue model training due to an internal error."}, 500

    def _save_dataset_temporarily(self, file_storage):
        """
        Saves the uploaded dataset file to a temporary directory.
        """
        temp_dir = tempfile.mkdtemp()
        dataset_name = file_storage.filename
        temp_file_path = os.path.join(temp_dir, dataset_name)
        file_storage.save(temp_file_path)
        return temp_dir, temp_file_path

    def _queue_training_request(self, model_id, temp_dir, temp_file_path, dataset_name,
                                image_size, batch_size, epochs, validation_split):
        """
        Adds the model training request to the training queue.
        """
        training_queue.put((model_id, {
            'temp_file_path': temp_file_path,
            'temp_dir': temp_dir,
            'dataset_name': dataset_name,
            'image_size': image_size,
            'batch_size': batch_size,
            'epochs': epochs,
            'validation_split': validation_split
        }))

    def process_training_request(self, model_id, details):
        """
        Processes the actual training request, including dataset preparation, model training,
        and storing the trained model and associated information.
        """
        try:
            dataset_path = details['temp_file_path']
            temp_dir = details['temp_dir']
            dataset_name = details['dataset_name']
            image_size = details['image_size']
            batch_size = details['batch_size']
            epochs = details['epochs']
            validation_split = details['validation_split']

            # Specify the MEGA folder to upload the dataset
            base_folder_name = f'{session["username"]}/{model_id}'
            # Find or create the MEGA folder to upload the dataset
            if not m.find(base_folder_name):
                m.create_folder(base_folder_name)
            dataset_folder_name = f'{session["username"]}/{model_id}/dataset'
            dataset_folder = m.create_folder(dataset_folder_name)
            # Upload the file to MEGA
            m.upload(dataset_path, dest=dataset_folder)

            # Save dataset location info on database
            from api.app import redis_db
            redis_db.hset("model:" + model_id, "dataset_location", dataset_folder_name)
            redis_db.hset("model:" + model_id, "dataset_name", dataset_name)

            # Extract and prepare dataset
            with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            unzipped_dataset_path = os.path.join(temp_dir, dataset_name[:-4])

            # Training process
            from train.cnn import CnnModel  # Import here to prevent circular imports
            cnn_model = CnnModel(model_id=model_id, image_size=image_size, dataset_path=unzipped_dataset_path,
                                 batch_size=batch_size, epochs=epochs, validation_split=validation_split)
            results_temp_path = cnn_model.run()

            # Update database and upload resulting files to MEGA
            redis_db.hset("model:" + model_id, "trained", str(True))
            modelfiles_folder_name = f'{session["username"]}/{model_id}/model_files'
            modelfiles_folder = m.create_folder(modelfiles_folder_name)
            model_file_path = os.path.join(results_temp_path, f"{model_id}.h5")
            m.upload(model_file_path, dest=modelfiles_folder)
            redis_db.hset("model:" + model_id, "model_files", modelfiles_folder_name)
            m.upload(os.path.join(results_temp_path, "class_labels.txt"), dest=modelfiles_folder)
            with open(os.path.join(results_temp_path, "report_data.json"), 'r') as report_file:
                report_data = report_file.read()
            redis_db.hset("model:" + model_id, "report_data", report_data)
            report_folder_name = f'{session["username"]}/{model_id}/report'
            report_folder = m.create_folder(report_folder_name)
            m.upload(os.path.join(results_temp_path, "accuracy_plot.png"), dest=report_folder)
            m.upload(os.path.join(results_temp_path, "loss_plot.png"), dest=report_folder)
            redis_db.hset("model:" + model_id, "report_plots", report_folder_name)
            training_params = {"image_size": image_size, "batch_size": batch_size, "epochs": epochs,
                               "validation_split": validation_split}
            redis_db.hset("model:" + model_id, "training_params", json.dumps(training_params))

            # Move report data and plots to temporary directory to later visualize
            dest_temp_dir = tempfile.mkdtemp()
            # Source file path
            data_source_file_path = os.path.join(results_temp_path, "report_data.json")
            # Destination file path in the new temporary directory
            data_destination_file_path = os.path.join(dest_temp_dir, "report_data.json")
            # Copy the file to the new temporary directory
            shutil.copy(data_source_file_path, data_destination_file_path)
            accuracy_source_file_path = os.path.join(results_temp_path, "accuracy_plot.png")
            loss_source_file_path = os.path.join(results_temp_path, "loss_plot.png")
            accuracy_destination_file_path = os.path.join(dest_temp_dir, "accuracy_plot.png")
            loss_destination_file_path = os.path.join(dest_temp_dir, "loss_plot.png")
            shutil.copy(accuracy_source_file_path, accuracy_destination_file_path)
            shutil.copy(loss_source_file_path, loss_destination_file_path)
            session['dest_temp_dir'] = dest_temp_dir

            # Delete temporary directories
            shutil.rmtree(temp_dir)
            shutil.rmtree(results_temp_path)

            logging.info(f"Model {model_id} trained and results stored successfully.")
        except Exception as e:
            logging.error(f"Error during training")