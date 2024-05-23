from PIL import Image
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
from pdf2image import convert_from_path
import tempfile
import os

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


