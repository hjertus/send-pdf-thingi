import time
import threading
from flask import Flask, request, send_file, abort
from dotenv import load_dotenv
import os

# Define the directory where you want to save the PDF
save_directory = 'pdf'

# Create the directory if it doesn't exist
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the secret key from the environment variables
valid_secret_key = os.getenv("SECRET_KEY")

# Replace this with the path to your PDF file
pdf_path = "pdf/pdf.pdf"

# Lock to synchronize access to the file
file_lock = threading.Lock()


def delete_file_after_delay():
    time.sleep(5)
    with file_lock:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


@app.route('/get_pdf', methods=['GET'])
def get_pdf():
    # Print all request headers for debugging
    print(f"Request Headers: {request.headers}")

    # Get the provided secret key from the request headers
    provided_secret_key = request.headers.get('Authorization')

    # Log the provided key for debugging
    print(f"Provided Secret Key: {provided_secret_key}")

    # Check if the provided key matches the valid key
    if provided_secret_key == f"Bearer {valid_secret_key}":
        try:
            if os.path.exists(pdf_path):
                print("The directory is not empty.")
                # If the key is valid, start a separate thread to delete the file after a delay
                threading.Thread(target=delete_file_after_delay).start()
                # Serve the PDF file
            return send_file(pdf_path, as_attachment=True)
        except Exception as e:
            # Handle any exceptions that may occur during the file serving
            print(f"An error occurred: {e}")
            abort(500)
    else:
        # If the key is not valid, log and return a 403 Forbidden response
        print("Invalid key provided.")
        abort(403)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)