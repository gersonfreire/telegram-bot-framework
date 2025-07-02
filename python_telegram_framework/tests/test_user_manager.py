import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tlgfwk.core.user_manager import UserManager
from tlgfwk.core.config import Config
from tlgfwk.core.persistence_manager import PersistenceManager

class TestUserManager(unittest.TestCase):

    def setUp(self):
        # Mock dependencies
        self.mock_persistence_manager = Mock(spec=PersistenceManager)
        self.mock_persistence_manager.load_data.return_value = {}
        
        self.mock_config = Mock(spec=Config)
        self.mock_config.owner_id = 123
        self.mock_config.admin_ids = [456]

        self.user_manager = UserManager(self.mock_persistence_manager, self.mock_config)

    def test_add_new_user(self):
        mock_user = MagicMock()
        mock_user.id = 789
        mock_user.username = 'testuser'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.is_bot = False
        mock_user.language_code = 'en'

        self.user_manager.add_or_update_user(mock_user)

        self.assertIn(789, self.user_manager.users)
        self.assertEqual(self.user_manager.users[789]['username'], 'testuser')
        self.mock_persistence_manager.save_data.assert_called_once()

    def test_is_owner(self):
        self.assertTrue(self.user_manager.is_owner(123))
        self.assertFalse(self.user_manager.is_owner(456))

    def test_is_admin(self):
        self.assertTrue(self.user_manager.is_admin(123))
        self.assertTrue(self.user_manager.is_admin(456))
        self.assertFalse(self.user_manager.is_admin(789))

if __name__ == '__main__':
    unittest.main()