

# Function to get input with timeout
import threading

def input_with_timeout(prompt, timeout=5, default=None):
    def input_thread(prompt, queue):
        queue.append(input(prompt))

    user_input = []
    input_thread = threading.Thread(target=input_thread, args=(prompt, user_input))
    input_thread.start()
    input_thread.join(timeout)

    if input_thread.is_alive():
        print("\nTimeout! No input received.")
        return default
    else:
        return user_input[0]

if __name__ == "__main__":

    # Example usage
    timeout_seconds = 5  # Set your timeout (seconds)
    user_input = input_with_timeout("Enter something: ", timeout_seconds)
    print("You entered:", user_input)    