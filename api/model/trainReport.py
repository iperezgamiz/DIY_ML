import base64
import os
import shutil
import logging
import json
from flask_restful import Resource
from flask import session, jsonify, url_for

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


class TrainReport(Resource):
    def get(self, model_id):
        """
        Returns the training report for a model, including base64-encoded plots for accuracy and loss.
        """
        try:
            dest_temp_dir = session.get('dest_temp_dir', '')
            if not dest_temp_dir or not os.path.exists(dest_temp_dir):
                logging.error("Session directory for model report not found.")
                return {"error": "Training report not available. Session or data may have expired."}, 404

            report_data = self._read_json_data(os.path.join(dest_temp_dir, "report_data.json"))
            accuracy_bytes = self._encode_image_to_base64(os.path.join(dest_temp_dir, "accuracy_plot.png"))
            loss_bytes = self._encode_image_to_base64(os.path.join(dest_temp_dir, "loss_plot.png"))

            # Clean up the temporary directory after reading the files
            shutil.rmtree(dest_temp_dir)
            session.pop('dest_temp_dir', None)

            return jsonify({
                "report_data": report_data,
                "accuracy_plot_base64": accuracy_bytes,
                "loss_plot_base64": loss_bytes
            })
        except Exception as e:
            logging.error(f"Failed to generate training report for model {model_id}: {e}")
            return {"error": "An unexpected error occurred while generating the training report."}, 500

    def post(self, model_id):
        """
        Redirects to a different endpoint for further actions.
        """
        # For RESTful APIs, consider returning the URL instead of redirecting.
        test_model_url = url_for('testmodel', model_id=model_id, _external=True)
        return jsonify({"next_step_url": test_model_url})

    @staticmethod
    def _read_json_data(file_path):
        """
        Reads and returns the content of a JSON file.
        """
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"JSON file not found at path: {file_path}")
            return {}

    @staticmethod
    def _encode_image_to_base64(image_path):
        """
        Encodes an image file to a base64 string.
        """
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            logging.error(f"Image file not found at path: {image_path}")
            return ""
