import fitz  # PyMuPDF
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import io
from PIL import Image

# Azure Computer Vision credentials
subscription_key = "ff0c5c0401b84667a46917d33068a3a4"
endpoint = "https://eastus.api.cognitive.microsoft.com/"

# Initialize Computer Vision client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode == "CMYK":
                image = image.convert("RGB")
            images.append((page_number + 1, img_index + 1, image))

    return images

def analyze_images(images):
    for page_number, img_index, image in images:
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            image_data = output.getvalue()

        analysis = computervision_client.analyze_image_in_stream(io.BytesIO(image_data), visual_features=["Description"])
        description = analysis.description.captions[0].text if analysis.description.captions else "No description available"
        print(f"Page {page_number} Image {img_index}: {description}")

# Path to your PDF file
pdf_path = "/Workspace/Users/nkumar3@rich.com/FIle_Path/Designing-reduced-fat-food-emulsions--Locust-bean-gum-fat_2013_Food-Hydrocol.pdf"

# Extract images from PDF
images = extract_images_from_pdf(pdf_path)

# Analyze images using Azure Computer Vision
analyze_images(images)
