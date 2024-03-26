import queue
import threading
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize queue for inference requests
# This queue holds inference requests to be processed by a separate thread
inference_queue = queue.Queue()


def process_inference_requests():
    """
    Continuously process inference requests from the inference queue.

    This function runs in a dedicated thread to handle inference requests asynchronously.
    It retrieves requests from the queue and uses the InferImage class to process each request.
    """
    while True:
        # Wait and get the next inference request from the queue
        model_id, args = inference_queue.get()
        try:
            # Import the InferImage class for inference processing
            from api.model.inference import InferImage
            infer_image = InferImage()
            logging.info(f"Processing inference request for model_id: {model_id}")

            # Process the inference request
            infer_image.process_inference_request(model_id, args)

        except Exception as e:
            # Log any exceptions that occur during the inference process
            logging.error(f"Error processing inference request for model_id {model_id}: {e}")

        finally:
            # Mark the inference request as done
            inference_queue.task_done()
            logging.info(f"Completed inference request for model_id: {model_id}")


def start_inference_thread():
    """
    Starts a thread dedicated to processing inference requests.

    This function creates and starts a daemon thread that runs the
    process_inference_requests function, enabling asynchronous processing
    of inference requests.

    Returns:
        threading.Thread: The created and started thread object.
    """
    logging.info("Starting inference processing thread.")
    inference_thread = threading.Thread(target=process_inference_requests)
    inference_thread.daemon = True  # Ensures thread does not prevent program termination
    inference_thread.start()
    return inference_thread

if __name__ == '__main__':
    start_inference_thread()
