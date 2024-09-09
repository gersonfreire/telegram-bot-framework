

# show all environment variables which exists on .env file

from dotenv import find_dotenv, dotenv_values, get_key

# Find the .env file
env_path = find_dotenv()

# Load the .env file into a dictionary
env_vars = dotenv_values(env_path)

# Key to check
key_to_check = 'MY_SECRET'

# Check if the key exists
if key_to_check in env_vars:
    print(f"{key_to_check} exists in the .env file.")
else:
    print(f"{key_to_check} does not exist in the .env file.")


def showenv():
    import os
    from dotenv import load_dotenv
    load_dotenv()

    for key in os.environ:
        # check if key exists on .env file, disabling the print of key not found in .env on this line
        # Load the .env file into a dictionary
        env_vars = dotenv_values(env_path)
        
        # if get_key('.env', key):
        #     print(f"{key}={os.getenv(key)}")
        
showenv()

