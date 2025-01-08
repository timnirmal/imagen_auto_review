
import requests
import io
import json
from PIL import Image
from logging_config import logger


# Example categories
CATEGORIES = {
    'T1': 'Text with correct spelling',
    'T2': 'Text with incorrect spelling',
    'W1': 'Watermark present',
    'H1': 'Contains humans',
    'N1': 'Contains nudity',
    'B1': 'Contains blood/violence',
    'BR': 'Contains brand logos',
    'CP': 'Copyright/movie content',
    'PL': 'Recognizable places',
    'PP': 'Recognizable people'
}

ANALYSIS_PROMPT = """
Analyze this image and check for the following:
1. Text content and spelling
2. Watermarks
3. Human presence
4. Nudity or inappropriate content
5. Blood or violence
6. Brand logos or trademarks
7. Copyright or movie content
8. Recognizable places
9. Recognizable people

Respond in this exact format (replace Yes/No with true/false):
{
    "text_present": Yes/No,
    "text_analysis": {
        "has_spelling_errors": Yes/No,
        "correct_spelling": Yes/No
    },
    "watermark_present": Yes/No,
    "contains_humans": Yes/No,
    "contains_nudity": Yes/No,
    "contains_blood_violence": Yes/No,
    "contains_brands": Yes/No,
    "copyright_content": Yes/No,
    "recognizable_places": Yes/No,
    "recognizable_people": Yes/No,
    "details": "Describe what you found here"
}
"""

import pycurl
from io import BytesIO

def download_image(url: str) -> bytes:
    """Download image from the URL using pycurl and return as bytes."""
    buffer = BytesIO()
    headers = [
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language: en-GB,en;q=0.9",
        "priority: u=0, i",
        "sec-ch-ua: \"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile: ?0",
        "sec-ch-ua-platform: \"Windows\"",
        "sec-fetch-dest: document",
        "sec-fetch-mode: navigate",
        "sec-fetch-site: none",
        "sec-fetch-user: ?1",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer: https://www.midjourney.com/"
    ]

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, headers)

    try:
        c.perform()
        c.close()
    except pycurl.error as e:
        c.close()
        raise RuntimeError(f"Failed to download image: {e}")

    return buffer.getvalue()


# Compress the image to reduce size
def compress_image(image_bytes: bytes, quality: int = 85) -> bytes:
    """Compress image bytes and return compressed bytes."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            format_ = img.format  # Preserve the image format
            with io.BytesIO() as output:
                img.save(output, format=format_, quality=quality)
                logger.info("Image compressed successfully.")
                return output.getvalue()
    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        return None

def default_json_error(details: str) -> dict:
    """Return a default JSON if something failed."""
    return {
        "text_present": False,
        "text_analysis": {
            "has_spelling_errors": False,
            "correct_spelling": False
        },
        "watermark_present": False,
        "contains_humans": False,
        "contains_nudity": False,
        "contains_blood_violence": False,
        "contains_brands": False,
        "copyright_content": False,
        "recognizable_places": False,
        "recognizable_people": False,
        "details": details
    }

# Clean and extract JSON from Gemini response
def clean_json_response(text: str) -> dict:
    """Parse JSON from the model's text response."""
    try:
        text = text.replace('```json', '').replace('```', '').strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end + 1]
            return json.loads(json_str)
        else:
            return {
                "text_present": False,
                "text_analysis": {
                    "has_spelling_errors": False,
                    "correct_spelling": False
                },
                "watermark_present": False,
                "contains_humans": False,
                "contains_nudity": False,
                "contains_blood_violence": False,
                "contains_brands": False,
                "copyright_content": False,
                "recognizable_places": False,
                "recognizable_people": False,
                "details": "Analysis failed - invalid JSON response."
            }
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return {
            "text_present": False,
            "text_analysis": {
                "has_spelling_errors": False,
                "correct_spelling": False
            },
            "watermark_present": False,
            "contains_humans": False,
            "contains_nudity": False,
            "contains_blood_violence": False,
            "contains_brands": False,
            "copyright_content": False,
            "recognizable_places": False,
            "recognizable_people": False,
            "details": f"Error parsing response: {e}"
        }

# Analyze the image
def analyze_image(image_bytes: bytes, genai_model) -> (str, str):
    """
    Analyze the image and return (categories, details).
    If an error occurs, return "error" as a category.
    """
    compressed_image_data = compress_image(image_bytes)
    if not compressed_image_data:
        return "error", "Failed to compress image."

    image = {
        'mime_type': f'image/{Image.open(io.BytesIO(compressed_image_data)).format.lower()}',
        'data': compressed_image_data
    }

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Send the image to the model for analysis
            response = genai_model.generate_content(contents=[ANALYSIS_PROMPT, image])
            analysis = clean_json_response(response.text)

            # Collect categories
            categories = []
            if analysis['text_present']:
                if analysis['text_analysis']['correct_spelling']:
                    categories.append('T1')
                if analysis['text_analysis']['has_spelling_errors']:
                    categories.append('T2')
            if analysis['watermark_present']:
                categories.append('W1')
            if analysis['contains_humans']:
                categories.append('H1')
            if analysis['contains_nudity']:
                categories.append('N1')
            if analysis['contains_blood_violence']:
                categories.append('B1')
            if analysis['contains_brands']:
                categories.append('BR')
            if analysis['copyright_content']:
                categories.append('CP')
            if analysis['recognizable_places']:
                categories.append('PL')
            if analysis['recognizable_people']:
                categories.append('PP')

            category_str = ', '.join(categories) if categories else 'Good'
            details_str = analysis.get('details', 'No details provided.')
            return category_str, details_str

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                return "error", f"Failed after {max_retries} retries: {e}"


# # Example usage
# if __name__ == "__main__":
#     from dotenv import load_dotenv
#
#     load_dotenv()
#
#     gemini_api_key = os.getenv("GEMINI_API_KEY", None)
#
#     # Configure Gemini with an API key
#     genai_model  = configure_gemini(gemini_api_key)
#
#     # Path to the image file
#     # image_path = "image.jpg"
#     image_path = "image2.jpg"
#
#     # Analyze the image
#     categories, details = analyze_image(image_path, genai_model)
#     logger.info(f"Categories: {categories}")
#     logger.info(f"Details: {details}")
#
#     print(categories)
#     print(details)