import time
import requests
from dotenv import load_dotenv
from brother_py import *
import tempfile
import os

# Define the directory where you want to save the PDF
save_directory = 'pdf'

# Create the directory if it doesn't exist
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
def check_website(url, secret_key, local_pdf_path):
    try:
        # Try to connect to the website
        response = requests.get(url)

        # Check if the website is accessible
        if response.status_code == 403:
            print("Website is accessible.")

            # Specify the actual path to the PDF file on the server
            pdf_url = url
            headers = {"Authorization": f"Bearer {secret_key}"}

            pdf_response = requests.get(pdf_url, headers=headers)

            # Print the response status code and content for debugging
            print(f"PDF Response Status Code: {pdf_response.status_code}")

            # Check if the PDF is accessible with the secret key
            if pdf_response.status_code == 200:
                print("PDF is accessible with the secret key.")

                # Save the PDF to the local directory
                with open(local_pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)

                print(f"PDF downloaded to {local_pdf_path}")
                convert_pdf_to_images_and_print(local_pdf_path)


            else:
                print("Failed to access the PDF with the secret key.")

        else:
            print(f"Website is not accessible. Status Code: {response.status_code}. Retrying...")

    except requests.ConnectionError:
        print("Failed to connect to the website. Retrying...")

# Example usage
website_url = "http://100.85.40.125:5000/get_pdf"

# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv("SECRET_KEY")
local_pdf_path = "pdf/pdf.pdf"  # Specify the local directory and filename

# Try to check the website and access the PDF
while True:
    check_website(website_url, secret_key, local_pdf_path)
    time.sleep(10)
