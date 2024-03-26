import requests
import os
import logging


def test_infer_image(model_id, image_file_path):
    """
    Sends an image file to the InferImage endpoint for inference.

    Args:
        model_id (str): The ID of the model to use for inference.
        image_file_path (str): Path to the image file to be sent for inference.
    """
    url = f"http://127.0.0.1:5000/model/{model_id}/inferImage"
    files = {'image_file': open(image_file_path, 'rb')}
    logging.info(f"Sending inference request for model {model_id} to {url}")

    try:
        response = requests.post(url, files=files)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


if __name__ == '__main__':
    model_id = 'example_model_id'  # Replace with your actual model ID
    image_file_path = 'path/to/image.jpg'  # Path to your image file

    # Ensure the image file exists
    if not os.path.exists(image_file_path):
        logging.error(f"Image file not found: {image_file_path}")
    else:
        response = test_infer_image(model_id, image_file_path)
        if response and response.status_code == 200:
            logging.info("Inference request processed successfully.")
            logging.info(f"Response: {response.json()}")
        elif response:
            logging.error(f"Failed to process inference request. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
        else:
            logging.error("Failed to receive any response from the server.")
