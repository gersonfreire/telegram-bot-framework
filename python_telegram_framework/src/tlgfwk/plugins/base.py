class PluginBase:
    """
    Base class for all plugins.

    Plugins should inherit from this class to be discoverable by the PluginManager.
    It provides access to the core framework components.

    Attributes:
        _is_plugin (bool): A class attribute to identify plugin classes.
        framework (TelegramBotFramework): The main framework instance.
        logger (logging.Logger): The framework's logger instance.
        config (Config): The framework's configuration object.
        user_manager (UserManager): The framework's user manager instance.
    """
    _is_plugin = True

    def __init__(self, framework):
        """
        Initializes the PluginBase.

        Args:
            framework (TelegramBotFramework): The main framework instance.
        """
        self.framework = framework
        self.logger = framework.logger
        self.config = framework.config
        self.user_manager = framework.user_manager

    def activate(self):
        """
        Called when the plugin is activated.
        Subclasses can override this method to perform setup tasks.
        """
        pass

    def deactivate(self):
        """
        Called when the plugin is deactivated.
        Subclasses can override this method to perform cleanup tasks.
        """
        pass