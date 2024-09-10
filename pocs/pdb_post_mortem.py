import pdb
import sys

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default excepthook for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(f"An unhandled exception occurred: {exc_value}")
    pdb.post_mortem(exc_traceback)

# Set the custom exception handler
sys.excepthook = handle_exception

def main():
    # Your code here
    print("Starting the script...")
    
    # Example code that raises an exception
    result = 10 / 0
    
    print("This line will not be executed due to the exception above.")

if __name__ == "__main__":
    main()
    
import pdb
import sys

def main():
    try:
        # Your code here
        print("Starting the script...")
        
        # Example code that raises an exception
        result = 10 / 0
        
        print("This line will not be executed due to the exception above.")
    
    except Exception as e:
        # Print the exception message
        print(f"An error occurred: {e}")
        
        # Start the debugger
        pdb.post_mortem()

if __name__ == "__main__":
    main()    