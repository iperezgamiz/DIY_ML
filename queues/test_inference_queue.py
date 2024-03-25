import unittest
from unittest.mock import patch, call
import logging
from queues.inference_queue import inference_queue, process_inference_requests, start_inference_thread

# Configure basic logging for the test execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestInferenceIntegration(unittest.TestCase):
    def setUp(self):
        """
        Prepare the environment for each test.

        Clears the inference queue to ensure a fresh start for each test case.
        """
        logging.info('Setting up test environment, clearing inference queue.')
        while not inference_queue.empty():
            inference_queue.get()

    @patch('api.model.inference.InferImage.process_inference_request')
    def test_multiple_inference_request_processing(self, mock_process_inference_request):
        """
        Test processing multiple inference requests in the queue.

        This test ensures that multiple requests can be added to the inference queue and
        are processed correctly by the inference processing thread, using a mock to avoid
        real inference processing.
        """
        # Setup mock to simulate the inference process without actually performing it
        mock_process_inference_request.return_value = None

        # Define mock inference requests to simulate input
        requests = [
            ("model_id_1", {'temp_dir': '/queues/temp_dir', 'image_name': 'descarga.jpg'}),
            ("model_id_1", {'temp_dir': '/queues/temp_dir', 'dataset_name': '0ee903ea13.jpg'})
        ]

        # Assert the queue is empty before test execution
        self.assertTrue(inference_queue.empty(), "Inference queue is not empty at start of test")

        # Add mock inference requests to the queue
        for request in requests:
            inference_queue.put(request)

        # Assert the queue is not empty after adding requests
        self.assertFalse(inference_queue.empty(), "Inference queue did not accept requests")

        # Start the thread for processing inference requests
        inference_thread = start_inference_thread()

        # Check that the processing thread is active
        self.assertTrue(inference_thread.is_alive(), "Inference processing thread did not start")

        # Wait for the thread to process the requests
        inference_thread.join(timeout=5)

        # Assert the queue is empty after processing, indicating that requests were handled
        self.assertTrue(inference_queue.empty(), "Inference queue is not empty after processing")

        # Verify that the mocked method was called with the correct arguments
        expected_calls = [call(*request) for request in requests]
        mock_process_inference_request.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(mock_process_inference_request.call_count, len(requests),
                         "Incorrect number of processed requests")

    def tearDown(self):
        """
        Clean up after each test.

        Ensures the inference queue is cleared and any background processing threads are stopped,
        preventing interference with subsequent tests.
        """
        logging.info('Tearing down test environment, clearing inference queue.')
        while not inference_queue.empty():
            inference_queue.get()


# Execute the test suite
if __name__ == '__main__':
    unittest.main()
