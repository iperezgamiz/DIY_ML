import json
import os
import shutil
import tempfile
import zipfile
import numpy as np
from PIL import Image
from flask import session
from flask_restful import Resource, reqparse
from keras.models import load_model
from mega import Mega
from werkzeug.datastructures import FileStorage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# Define argument parser for testing model endpoint
testModel_args = reqparse.RequestParser()
testModel_args.add_argument('test_dataset', location='files', type=FileStorage, required=True)

# MEGA access credentials and login
EMAIL = 'your_email@gmail.com'
PASSWORD = 'your_password'
mega = Mega()
m = mega.login(EMAIL, PASSWORD)


class TestModel(Resource):
    def post(self, model_id):
        """
        Tests a trained model with a provided dataset, calculating the Correct Classification Rate (CCR).
        """
        try:

            # Setup a temporary directory for handling files
            temp_dir = tempfile.mkdtemp()
            model, class_labels = self._download_model_and_labels(model_id, temp_dir)

            # Get test dataset
            args = testModel_args.parse_args()
            test_dataset = args["test_dataset"]
            test_dataset_name = test_dataset.filename
            test_dataset_path = os.path.join(temp_dir, test_dataset_name)
            test_dataset.save(temp_dir)
            # Unzip test dataset
            unzipped_dataset_path = self._unzip_test_dataset(test_dataset_path, test_dataset_name, temp_dir)

            from api.app import redis_db
            training_params = json.loads(redis_db.hget("model:" + model_id, "training_params"))
            image_size = training_params["image_size"]
            image_size_1 = image_size[0]
            image_size_2 = image_size[1]
            image_size = (int(image_size_1), int(image_size_2))
            # Calculate CCR
            ccr = self._calculate_ccr(model, class_labels, unzipped_dataset_path, image_size)

            # Cleanup temporary directory
            shutil.rmtree(temp_dir)

            logging.info(f"Model {model_id} tested successfully with CCR: {ccr}")
            return {"message": "Test completed successfully.", "CCR": ccr}, 200
        except Exception as e:
            logging.error(f"Failed to test model {model_id}: {e}")
            return {"error": "An unexpected error occurred during the model test."}, 500

    def _download_model_and_labels(self, model_id, temp_dir):
        """
        Downloads the model and class labels from storage.
        """
        from api.app import redis_db
        model_loc = redis_db.hget("model:" + model_id, "model_files")
        modelfile_loc = model_loc + f'{model_id}.h5'
        modelfile = m.find(modelfile_loc)
        modelfile.download(temp_dir)
        model_path = os.path.join(temp_dir, f"{model_id}.h5")
        # Load the model
        model = load_model(model_path)

        class_labels_loc = model_loc + "class_labels.txt"
        class_labels_file = m.find(class_labels_loc)
        class_labels_file.download(temp_dir)
        class_labels_path = os.path.join(temp_dir, "class_labels.txt")
        with open(class_labels_path, "r") as f:
            class_labels = f.read().splitlines()
        return model, class_labels

    def _unzip_test_dataset(self, test_dataset_path, test_dataset_name, temp_dir):
        """
        Unzips the test dataset.
        """
        with zipfile.ZipFile(test_dataset_path, 'r') as zip_ref:
            # Extract all contents to the specified directory
            zip_ref.extractall(temp_dir)
        return os.path.join(temp_dir, test_dataset_name[:-4])

    def _calculate_ccr(self, model, class_labels, unzipped_dataset_path, image_size):
        """
        Calculates the Correct Classification Rate (CCR) for the test dataset.
        """

        ccr = 0
        n_images = 0
        for image_class in os.listdir(unzipped_dataset_path):
            for image in os.listdir(os.path.join(unzipped_dataset_path, image_class)):
                n_images += 1
                image_path = os.path.join(unzipped_dataset_path, image_class, image)
                img = Image.open(image_path)
                img = img.resize(image_size)  # Resize the image to match the input size of the model
                img_array = np.array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array.astype('float32') / 255.  # Normalize the image

                # Make prediction
                prediction = model.predict(img_array)

                # Get the predicted class index
                predicted_class_index = np.argmax(prediction)

                # Get the predicted class label
                predicted_class_label = class_labels[predicted_class_index]

                if predicted_class_label == image_class:
                    ccr += 1

        ccr = ccr / n_images
        session["ccr"] = ccr
        return ccr
