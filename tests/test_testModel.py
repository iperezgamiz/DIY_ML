import requests
import os
import logging


def test_model(model_id, test_dataset_path):
    url = f"http://127.0.0.1:5000/model/{model_id}/testModel"
    files = {'test_dataset': open(test_dataset_path, 'rb')}
    logging.info(f"Sending test dataset to {url}")

    try:
        response = requests.post(url, files=files)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


if __name__ == '__main__':
    model_id = 'model_id'  # Replace with your actual model ID
    test_dataset_path = 'test_dataset.zip'  # Path to your test dataset

    # Ensure the test dataset exists
    if not os.path.exists(test_dataset_path):
        logging.error(f"Test dataset not found: {test_dataset_path}")
    else:
        response = test_model(model_id, test_dataset_path)
        if response and response.status_code == 200:
            logging.info("Test completed successfully.")
            logging.info(f"Response: {response.json()}")
        elif response:
            logging.error(f"Failed to test model. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
        else:
            logging.error("Failed to receive any response from the server.")
