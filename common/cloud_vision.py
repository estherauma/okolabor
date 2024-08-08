import os
from pathlib import Path
from google.cloud import vision
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "jaguar-420513-e6e93068b07e.json"
def detect_text_in_image(image_path):
    # Instantiate a client
    client = vision.ImageAnnotatorClient()

    # Load the image from the local file system
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Detect text in the image
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}')

    print('Detected text:')
    for text in texts:
        print(f'\n"{text.description}"')

# Replace 'path_to_your_image' with the actual file path to your image
detect_text_in_image('passport.jpeg')
