import unittest
import requests
import os
import logging

class TestTrainModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup logging only once for all tests
        logging.basicConfig(level=logging.INFO)

    def test_train_model(self):
        """
        Test sending a POST request to train a model with specified parameters.
        """
        # Example parameters
        model_id = 'example_model_id'
        dataset_file_path = 'path/to/dataset.zip'
        image_size = (128, 128)
        batch_size = 32
        epochs = 10
        validation_split = 0.2

        url = f"http://127.0.0.1:5000/model/{model_id}/trainModel"
        data = {
            'image_size_1': image_size[0],
            'image_size_2': image_size[1],
            'batch_size': batch_size,
            'epochs': epochs,
            'validation_split': validation_split
        }

        # Ensure the dataset file exists
        self.assertTrue(os.path.exists(dataset_file_path), f"Dataset file not found: {dataset_file_path}")

        with open(dataset_file_path, 'rb') as dataset_file:
            files = {'dataset_file': dataset_file}
            logging.info(f"Sending training request for model {model_id} to {url}")

            try:
                response = requests.post(url, files=files, data=data)
                # Check if the request was successful
                self.assertEqual(response.status_code, 202, "Failed to initiate model training")
                logging.info("Model training initiated successfully.")
                logging.info(f"Response: {response.json()}")
            except requests.exceptions.RequestException as e:
                self.fail(f"Request failed: {e}")

if __name__ == '__main__':
    unittest.main()
