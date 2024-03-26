import requests
import os
import logging


def test_train_model(model_id, dataset_file_path, image_size, batch_size, epochs, validation_split):
    """
    Sends a POST request to train a model with the specified parameters.

    Args:
        model_id (str): The ID of the model to train.
        dataset_file_path (str): Path to the zip file containing the dataset.
        image_size (tuple): The dimensions to which images will be resized.
        batch_size (int): The number of samples per gradient update.
        epochs (int): The number of epochs to train the model.
        validation_split (float): The fraction of the data to use as validation set.
    """
    url = f"http://127.0.0.1:5000/model/{model_id}/trainModel"
    files = {'dataset_file': open(dataset_file_path, 'rb')}
    data = {
        'image_size_1': image_size[0],
        'image_size_2': image_size[1],
        'batch_size': batch_size,
        'epochs': epochs,
        'validation_split': validation_split
    }
    logging.info(f"Sending training request for model {model_id} to {url}")

    try:
        response = requests.post(url, files=files, data=data)
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


if __name__ == '__main__':
    # Example parameters
    model_id = 'example_model_id'
    dataset_file_path = 'path/to/dataset.zip'
    image_size = (128, 128)
    batch_size = 32
    epochs = 10
    validation_split = 0.2

    # Ensure the dataset file exists
    if not os.path.exists(dataset_file_path):
        logging.error(f"Dataset file not found: {dataset_file_path}")
    else:
        response = test_train_model(model_id, dataset_file_path, image_size, batch_size, epochs, validation_split)
        if response and response.status_code == 202:
            logging.info("Model training initiated successfully.")
            logging.info(f"Response: {response.json()}")
        elif response:
            logging.error(f"Failed to initiate model training. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
        else:
            logging.error("Failed to receive any response from the server.")
