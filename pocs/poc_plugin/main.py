# from plugin_manager import import_module

# Import the multiply function from the helper module in the utils package
import importlib


helper_module = importlib.import_module('.helper', package='utils')
multiply = getattr(helper_module, 'multiply')

# Use the multiply function
result = multiply(2, 3)
print(result)  # Output: 6