from PyPDF2 import PdfReader, PdfWriter
from flask import Flask, render_template, redirect, url_for, request
import os
import requests

# Define the directory where you want to save the PDF
save_directory = 'pdf'

# Create the directory if it doesn't exist
if not os.path.exists(save_directory):
    os.makedirs(save_directory)


app = Flask(__name__)

@app.route('/upload/<path:url_for_pdf>', methods=['GET'])
def upload_from_url(url_for_pdf):
    try:
        # Define the path where you want to save the PDF
        save_path = os.path.join(save_directory, 'pdf.pdf')

        # Download PDF from the provided URL and save it directly to the pdf directory
        response = requests.get(url_for_pdf, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Return a response or redirect as needed
        return "Processing complete!"

    except requests.RequestException as e:
        return f"Failed to download PDF from {url_for_pdf}. Error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return redirect(request.url)

        pdf_file = request.files['pdf']

        if pdf_file.filename == '':
            return redirect(request.url)

        if pdf_file:
            # Save the PDF in the same directory as the script
            pdf_path = f'{save_directory}/pdf.pdf'

            if not os.path.exists(pdf_path):
                pdf_file.save(pdf_path)
                print("File saved successfully.")
            else:
                print("File already exists. Merging...")
                temp_pdf = f'{save_directory}/temp.pdf'
                pdf_file.save(temp_pdf)

                # Load existing PDF
                existing_pdf = PdfReader(pdf_path)
                existing_pages = existing_pdf.pages

                # Load new PDF
                new_pdf = PdfReader(temp_pdf)
                new_pages = new_pdf.pages

                # Create a writer object for writing to the existing PDF
                writer = PdfWriter()

                # Add existing pages to the writer
                for page in existing_pages:
                    writer.add_page(page)

                # Add new pages to the writer
                for page in new_pages:
                    writer.add_page(page)

                # Write the combined pages to the existing PDF file
                with open(pdf_path, "wb") as f:
                    writer.write(f)

                os.remove(temp_pdf)

                print("Files merged successfully.")

            # Redirect back to the first page with an empty file input field
            return redirect(url_for('upload_pdf'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)