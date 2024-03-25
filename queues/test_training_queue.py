import unittest
from unittest.mock import patch, call
import logging
from queues.training_queue import training_queue, process_training_requests, start_training_thread

# Configure basic logging for test execution
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestTrainingIntegration(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment before each test.

        This clears the training queue to ensure a fresh environment for each test case.
        """
        logging.info('Setting up test environment: Clearing the training queue.')
        while not training_queue.empty():
            training_queue.get()

    @patch('api.model.trainModel.TrainModel.process_training_request')
    def test_multiple_training_request_processing(self, mock_process_training_request):
        """
        Test the processing of multiple training requests in the training queue.

        This test simulates adding multiple training requests to the queue and verifies
        that they are processed correctly using a mocked version of the training process.
        """
        # Setup mock to simulate the training process without executing it
        mock_process_training_request.return_value = None

        # Define mock training requests with varying parameters to simulate different training scenarios
        requests = [
            ("model_id_1", {
                'temp_file_path': '/queues/temp_dir/dataset_1.zip',
                'temp_dir': '/queues/temp_dir',
                'dataset_name': 'dataset_1',
                'image_size': (64, 64),
                'batch_size': 32,
                'epochs': 10,
                'validation_split': 0.2
            }),
            ("model_id_2", {
                'temp_file_path': '/queues/temp_dir/dataset_2.zip',
                'temp_dir': '/queues/temp_dir',
                'dataset_name': 'dataset_2',
                'image_size': (128, 128),
                'batch_size': 64,
                'epochs': 5,
                'validation_split': 0.3
            })
        ]

        # Ensure the queue is empty before test execution
        self.assertTrue(training_queue.empty(), "Training queue was not empty at the start of the test")

        # Add the mock training requests to the queue
        for request in requests:
            training_queue.put(request)

        # Verify the queue is populated with the requests
        self.assertFalse(training_queue.empty(), "Training queue did not receive the requests")

        # Start the training processing thread
        training_thread = start_training_thread()
        logging.info('Started the training processing thread.')

        # Check that the thread is active
        self.assertTrue(training_thread.is_alive(), "Training processing thread is not alive")

        # Wait for the thread to process the requests (with a timeout to prevent hanging)
        training_thread.join(timeout=5)

        # After processing, the queue should be empty
        self.assertTrue(training_queue.empty(), "Training queue is not empty after processing")

        # Verify the mocked training process was called with the correct arguments
        expected_calls = [call(*request) for request in requests]
        mock_process_training_request.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(mock_process_training_request.call_count, len(requests),
                         "Mocked training process was not called the expected number of times")

    def tearDown(self):
        """
        Clean up the test environment after each test.

        Clears the training queue and ensures no training processes are left hanging.
        """
        logging.info('Tearing down test environment: Clearing the training queue.')
        while not training_queue.empty():
            training_queue.get()


if __name__ == '__main__':
    unittest.main()
