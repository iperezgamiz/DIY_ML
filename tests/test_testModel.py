import unittest
import requests
import os
import logging


class TestModelEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    def test_model(self):
        """
        Sends a test dataset to the specified model's testModel endpoint
        and checks for successful completion.
        """
        model_id = 'model_id'  # Replace with actual model ID
        test_dataset_path = 'test_dataset.zip'  # Path to test dataset

        # Ensure the test dataset exists
        self.assertTrue(os.path.exists(test_dataset_path), f"Test dataset not found: {test_dataset_path}")

        url = f"http://127.0.0.1:5000/model/{model_id}/testModel"
        logging.info(f"Sending test dataset to {url}")

        try:
            with open(test_dataset_path, 'rb') as test_dataset:
                files = {'test_dataset': test_dataset}
                response = requests.post(url, files=files)
                # Check if the request was successful
                self.assertEqual(response.status_code, 200, "Failed to test model")
                logging.info("Test completed successfully.")
                logging.info(f"Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    unittest.main()
