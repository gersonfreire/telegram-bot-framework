import pickle
import os
import json
from ..utils.logger import get_logger

class PersistenceManager:
    """
    Manages data persistence for the bot, supporting multiple backends.

    This class provides a simple interface for saving and loading data,
    abstracting the underlying storage mechanism.

    Supported backends:
    - pickle: For serializing Python objects.
    - json: For human-readable data storage.

    Attributes:
        storage_path (str): The directory where data files are stored.
        logger (logging.Logger): The logger instance.
    """
    def __init__(self, storage_path='data/'):
        """
        Initializes the PersistenceManager.

        Args:
            storage_path (str): The path to the storage directory.
        """
        self.storage_path = storage_path
        self.logger = get_logger(__name__)
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def _get_path(self, filename):
        """Constructs the full path for a given filename."""
        return os.path.join(self.storage_path, filename)

    def save_data(self, filename, data, backend='pickle'):
        """Saves data to a file using the specified backend."""
        path = self._get_path(filename)
        try:
            if backend == 'pickle':
                with open(path, 'wb') as f:
                    pickle.dump(data, f)
            elif backend == 'json':
                with open(path, 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                raise ValueError(f"Unsupported backend: {backend}")
            self.logger.debug(f"Data saved to {path} using {backend}.")
        except (IOError, pickle.PicklingError, json.JSONDecodeError) as e:
            self.logger.error(f"Error saving data to {path}: {e}")

    def load_data(self, filename, default=None, backend='pickle'):
        """Loads data from a file using the specified backend."""
        path = self._get_path(filename)
        if not os.path.exists(path):
            return default
        
        try:
            if backend == 'pickle':
                with open(path, 'rb') as f:
                    return pickle.load(f)
            elif backend == 'json':
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                raise ValueError(f"Unsupported backend: {backend}")
        except (IOError, pickle.UnpicklingError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading data from {path}: {e}")
            return default