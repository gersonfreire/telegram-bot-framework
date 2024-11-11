import unittest
from unittest.mock import patch, MagicMock
from util_watch import check_port

class TestUtilWatch(unittest.TestCase):

    @patch('socket.socket')
    def test_check_port_open(self, mock_socket):
        # Mock the socket instance
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate successful connection
        mock_socket_instance.connect.return_value = None

        result = check_port('127.0.0.1', 80)
        self.assertTrue(result)
        mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 80))
        mock_socket_instance.shutdown.assert_called_once()
        mock_socket_instance.close.assert_called_once()

    @patch('socket.socket')
    def test_check_port_closed(self, mock_socket):
        # Mock the socket instance
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Simulate failed connection
        mock_socket_instance.connect.side_effect = Exception('Connection failed')

        result = check_port('127.0.0.1', 80)
        self.assertFalse(result)
        mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 80))
        mock_socket_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()