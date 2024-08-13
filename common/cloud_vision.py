import os
import re
from pathlib import Path
from google.cloud import vision
from decouple import config

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config('CREDS_FILE_PATH')

def detect_text_in_image(image_path):
    client = vision.ImageAnnotatorClient()

    # Load the image from the local file system
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}')

    response = []
    for text in texts:
      response.append(text.description)
    return response

