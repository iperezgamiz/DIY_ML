import queue
import threading
import logging

# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize queue for training requests
# This queue holds training requests to be processed by a separate thread
training_queue = queue.Queue()


def process_training_requests():
    """
    Continuously process training requests from the training queue.

    This function retrieves training requests from the queue and uses the TrainModel class
    to handle each request. It runs in a dedicated thread to allow asynchronous processing.
    """
    while True:
        try:
            # Wait and get the next training request from the queue
            model_id, args = training_queue.get()

            # Dynamically import the TrainModel class for handling the training request
            from api.model.trainModel import TrainModel
            train_model = TrainModel()

            logging.info(f"Starting training process for model_id: {model_id}")
            # Process the training request
            train_model.process_training_request(model_id, args)
            logging.info(f"Completed training process for model_id: {model_id}")

        except Exception as e:
            # Log any exceptions that occur during the training process
            logging.error(f"Error during training process for model_id {model_id}: {e}")

        finally:
            # Mark the training request as done
            training_queue.task_done()


def start_training_thread():
    """
    Starts a thread dedicated to processing training requests.

    This function creates and starts a daemon thread that runs the process_training_requests
    function, enabling asynchronous processing of training requests.

    Returns:
        threading.Thread: The thread object that has been started.
    """
    logging.info("Starting training processing thread.")
    training_thread = threading.Thread(target=process_training_requests)
    training_thread.daemon = True  # Ensures the thread does not prevent program termination
    training_thread.start()
    return training_thread


# Example of starting the training thread
if __name__ == '__main__':
    start_training_thread()
    # Example usage could include adding training requests to the queue here
