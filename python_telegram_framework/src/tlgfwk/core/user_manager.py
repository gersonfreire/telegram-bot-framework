import datetime
from ..utils.logger import get_logger

class UserManager:
    """
    Manages user registration, tracking, and administration.
    """
    def __init__(self, persistence_manager, config):
        self.persistence = persistence_manager
        self.config = config
        self.logger = get_logger(__name__)
        self.users = self.persistence.load_data('users.pkl', default={})

    def get_user(self, user_id):
        """Retrieves a user by their ID."""
        return self.users.get(user_id)

    def add_or_update_user(self, user):
        """Adds a new user or updates an existing one."""
        user_id = user.id
        if user_id not in self.users:
            self.users[user_id] = {
                'id': user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_bot': user.is_bot,
                'language_code': user.language_code,
                'first_seen': datetime.datetime.now(),
                'last_seen': datetime.datetime.now(),
                'interactions': 0,
                'history': []
            }
            self.logger.info(f"New user registered: {user_id} ({user.username})")
        else:
            self.users[user_id]['last_seen'] = datetime.datetime.now()
            self.users[user_id]['interactions'] += 1
        
        self.save_users()
        return self.users[user_id]

    def record_interaction(self, user_id, command):
        """Records a user interaction."""
        if user_id in self.users:
            self.users[user_id]['history'].append({
                'timestamp': datetime.datetime.now(),
                'command': command
            })
            self.save_users()

    def is_owner(self, user_id):
        """Checks if a user is the bot owner."""
        return user_id == self.config.owner_id

    def is_admin(self, user_id):
        """Checks if a user is an admin."""
        return user_id in self.config.admin_ids or self.is_owner(user_id)

    def add_admin(self, user_id):
        """Adds a new admin."""
        if user_id not in self.config.admin_ids:
            self.config.admin_ids.append(user_id)
            # In a real implementation, this should also update the .env file
            self.logger.info(f"User {user_id} added as admin.")
            return True
        return False

    def remove_admin(self, user_id):
        """Removes an admin."""
        if user_id in self.config.admin_ids:
            self.config.admin_ids.remove(user_id)
            self.logger.info(f"User {user_id} removed from admins.")
            return True
        return False

    def list_users(self):
        """Lists all registered users."""
        return self.users.values()

    def save_users(self):
        """Saves the user data to the persistence backend."""
        self.persistence.save_data('users.pkl', self.users)