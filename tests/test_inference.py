import unittest
import requests
import logging


class TestInferImage(unittest.TestCase):
    def test_infer_image(self):
        """
        Test sending an image file to the InferImage endpoint for inference.
        """
        model_id = 'model_id_1'  # Replace with your actual model ID
        image_file_path = 'tests/descarga.jpg'  # Path to your image file

        url = f"http://127.0.0.1:5000/model/{model_id}/inferImage"
        with open(image_file_path, 'rb') as image_file:
            files = {'image_file': image_file}
            logging.info(f"Sending inference request for model {model_id} to {url}")

            try:
                response = requests.post(url, files=files)
                self.assertEqual(response.status_code, 200)
                logging.info("Inference request processed successfully.")
                logging.info(f"Response: {response.json()}")
            except requests.exceptions.RequestException as e:
                self.fail(f"Request failed: {e}")


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    unittest.main()
