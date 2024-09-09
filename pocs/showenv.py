

# show all environment variables which exists on .env file
from dotenv import get_key


def showenv():
    import os
    from dotenv import load_dotenv
    load_dotenv()

    for key in os.environ:
        # check if key exists on .env file
        if get_key('.env', key):
            print(f"{key}={os.getenv(key)}")
        
showenv()

