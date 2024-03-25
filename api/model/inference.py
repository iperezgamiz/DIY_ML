import json
import os
import tempfile
import logging
import numpy as np
from PIL import Image
from flask_restful import Resource, reqparse
from mega import Mega
from werkzeug.datastructures import FileStorage
from keras.models import load_model
from queues.inference_queue import inference_queue
from flask import jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)

# Setup argument parsing for inference requests
inference_args = reqparse.RequestParser()
inference_args.add_argument('image_file', location='files', type=FileStorage, required=True)

# MEGA access credentials (Placeholder values)
EMAIL = 'your_email@gmail.com'
PASSWORD = 'your_password'

# Initialize MEGA API client
mega = Mega()
m = mega.login(EMAIL, PASSWORD)


class InferImage(Resource):
    def post(self, model_id):
        try:
            # Parse incoming request arguments
            args = inference_args.parse_args()
            image_file = args["image_file"]

            # Create a temporary directory to store the incoming file
            temp_dir = tempfile.mkdtemp()
            image_path = os.path.join(temp_dir, image_file.filename)
            image_file.save(image_path)

            logging.info("Image saved to temporary directory")

            # Add inference request to the processing queue
            inference_queue.put((model_id, {
                'temp_dir': temp_dir,
                'image_name': image_file.filename,
            }))

            return jsonify({"message": "Inference request received"}), 200
        except Exception as e:
            logging.error(f"Error processing inference request: {str(e)}")
            return jsonify({"error": "Failed to process inference request"}), 500

    def process_inference_request(self, model_id, args):
        try:
            temp_dir = args['temp_dir']
            image_name = args['image_name']

            # Retrieve model location from Redis
            from api.app import redis_db
            model_loc = redis_db.hget("model:" + model_id, "model_files")
            modelfile_loc = os.path.join(model_loc, f'{model_id}.h5')

            # Download model file from MEGA
            modelfile = m.find(modelfile_loc)
            modelfile.download(temp_dir)
            logging.info("Model file downloaded")

            model_path = os.path.join(temp_dir, f"{model_id}.h5")
            model = load_model(model_path)
            logging.info("Model loaded")

            # Download class labels
            class_labels_loc = os.path.join(model_loc, "class_labels.txt")
            class_labels_file = m.find(class_labels_loc)
            class_labels_file.download(temp_dir)

            class_labels_path = os.path.join(temp_dir, "class_labels.txt")
            with open(class_labels_path, "r") as f:
                class_labels = f.read().splitlines()

            # Process the image and prepare for prediction
            training_params = json.loads(redis_db.hget("model:" + model_id, "training_params"))
            image_size = (int(training_params["image_size"][0]), int(training_params["image_size"][1]))

            image_path = os.path.join(temp_dir, image_name)
            img = Image.open(image_path).resize(image_size)
            img_array = np.expand_dims(np.array(img), axis=0).astype('float32') / 255.

            # Make prediction
            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction)
            predicted_class_label = class_labels[predicted_class_index]

            return {"Predicted class label": predicted_class_label}
        except Exception as e:
            logging.error(f"Error during inference processing: {str(e)}")
