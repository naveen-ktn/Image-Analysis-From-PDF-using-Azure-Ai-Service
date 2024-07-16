from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import time

# Set your Azure Computer Vision credentials
subscription_key = "ff0c5c0401b84667a46917d33068a3a4"
endpoint = "https://eastus.api.cognitive.microsoft.com/"

# Create a Computer Vision client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def extract_images_from_pdf(pdf_path, output_folder):
    # Open the PDF file
    document = fitz.open(pdf_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_counter = 1

    for page_number in range(len(document)):
        page = document.load_page(page_number)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_path = os.path.join(output_folder, f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}")

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Open the image
            with open(image_path, "rb") as image_stream:
                image = Image.open(image_stream)

                # Check if the image meets the minimum size requirement
                if image.width >= 50 and image.height >= 50:
                    image_stream.seek(0)  # Reset stream pointer to the beginning
                    try:
                        # Use the Computer Vision SDK to analyze the image
                        analysis = computervision_client.read_in_stream(image_stream, raw=True)

                        # Extract the operation location (URL with an ID at the end) from the response
                        operation_location = analysis.headers["Operation-Location"]
                        operation_id = operation_location.split("/")[-1]

                        # Wait for the operation to complete
                        while True:
                            result = computervision_client.get_read_result(operation_id)
                            if result.status not in ['notStarted', 'running']:
                                break
                            time.sleep(1)

                        # Get the text from the result
                        if result.status == OperationStatusCodes.succeeded:
                            read_results = result.analyze_result.read_results
                            for read_result in read_results:
                                for line in read_result.lines:
                                    print(line.text)
                    except Exception as e:
                        print(f"Error processing image {image_path}: {e}")
                else:
                    print(f"Image {image_path} is too small (width: {image.width}, height: {image.height}). Skipping.")

# Example usage
pdf_path = "/Users/naveen/FIle_Path/Designing-reduced-fat-food-emulsions--Locust-bean-gum-fat_2013_Food-Hydrocol.pdf"
output_folder = "/Users/naveen/FIle_Path/Result_Image"
extract_images_from_pdf(pdf_path, output_folder)
