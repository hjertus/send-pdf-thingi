import time
from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
from pdf2image import convert_from_path
import requests
from dotenv import load_dotenv
import tempfile
import os

# Define the directory where you want to save the PDF
save_directory = 'pdf'

# Create the directory if it doesn't exist
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def convert_pdf_to_images_and_print(pdf_path):
    # Create a temporary directory to store the PDF and images
    temp_dir = tempfile.mkdtemp()

    # Convert PDF pages to images
    pdf_images = convert_from_path(pdf_path)

    for i, pdf_image in enumerate(pdf_images):
        images = []  # Initialize an empty list to store stretched images
        # Save each page as an image
        img_path = os.path.join(temp_dir, f'receipt_{i}.jpg')
        pdf_image.save(img_path, 'JPEG')

        # Open the saved image using PIL
        image = Image.open(img_path)

        # Define the desired fixed width and height
        fixed_width = 1200
        fixed_height = 1822

        # Crop and resize the image
        stretched_image = crop_and_resize_image(image, fixed_width, fixed_height)

        # Append the stretched image to the list
        images.append(stretched_image)
        try:
            printing(images)
        except Exception as e:
            print(f"Failed to print {e}")


def printing(images):
    # Setting Printer Specifications
    backend = 'pyusb'
    model = 'QL-1100'
    printer = 'usb://0x04F9:0x20A7/000/001'

    # Initialize BrotherQLRaster with the specified model
    qlr = BrotherQLRaster(model)
    qlr.exception_on_warning = True

    # Converting print instructions for the Brother printer
    instructions = convert(
        qlr=qlr,
        images=images,  # Pass the list of stretched images
        label='103x164',  # Use the appropriate label size
        rotate='0',  # 'Auto', '0', '90', '270'
        threshold=70.0,  # Black and white threshold in percent.
        dither=False,
        compress=False,
        dpi_600=False,
        hq=True,  # False for low quality.
        cut=True
    )

    # Send the instructions to the printer
    send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)

def crop_and_resize_image(image, fixed_width, fixed_height):
    # Get the dimensions of the image
    width, height = image.size

    # Calculate the number of rows (pixels) to remove from the top 10%
    rows_to_remove = int(height * 0.08)

    # Crop the image to remove the top 10%
    cropped_image = image.crop((0, rows_to_remove, width, height))

    # Resize the cropped image to the fixed width and height
    stretched_image = cropped_image.resize((fixed_width, fixed_height))

    return stretched_image



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
website_url = "http://10.255.0.150:5000/get_pdf"

# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv("SECRET_KEY")
local_pdf_path = "pdf/pdf.pdf"  # Specify the local directory and filename

# Try to check the website and access the PDF
while True:
    check_website(website_url, secret_key, local_pdf_path)
    time.sleep(10)
