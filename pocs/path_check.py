import os

# Replace with your path
path = "/path/file"

# Print the path to ensure it is correct
print(f"Checking path: '{path}'")

# Check if the path exists
if os.path.exists(path):
    print("Path exists.")
else:
    print("Path does not exist.")

# Additional checks
print(f"Absolute path: {os.path.abspath(path)}")
print(f"Is absolute: {os.path.isabs(path)}")
print(f"Is directory: {os.path.isdir(path)}")
print(f"Is file: {os.path.isfile(path)}")