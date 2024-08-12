import os
import re
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

def extract_passport_info(text):
    passport_info = {}

    # Regex patterns for matching specific fields
    passport_number_pattern = r"Passport\s?No\.?\s*([A-Z0-9]+)"
    gender_pattern = r"Gender\s*:\s*(Male|Female|M|F)"
    nationality_pattern = r"Nationality\s*:\s*([A-Za-z]+)"

    # Search for Passport Number
    passport_number_match = re.search(passport_number_pattern, text)
    if passport_number_match:
        passport_info['Passport Number'] = passport_number_match.group(1)

    # Search for Gender
    gender_match = re.search(gender_pattern, text, re.IGNORECASE)
    if gender_match:
        passport_info['Gender'] = gender_match.group(1)

    # Search for Nationality
    nationality_match = re.search(nationality_pattern, text, re.IGNORECASE)
    if nationality_match:
        passport_info['Nationality'] = nationality_match.group(1)

    # Add more patterns as needed

    return passport_info

# Replace 'path_to_your_image' with the actual file path to your image
text = detect_text_in_image('passport.jpeg')
passport_info = extract_passport_info(text)

print("Extracted Passport Information:")
for label, value in passport_info.items():
    print(f"{label}: {value}")
