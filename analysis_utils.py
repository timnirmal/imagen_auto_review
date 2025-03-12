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
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
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

def validate_image(image_data: bytes) -> bool:
    """Validate if the image is readable and not corrupted."""
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()  # Check for corruption
        logger.info(f"Image validation successful. Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def fetch_image(url: str) -> bytes:
    """Download image from URL."""
    try:
        return download_image(url)
    except Exception as e:
        logger.error(f"Failed to download image from URL: {e}")
        raise RuntimeError("Image redownload failed")

# Analyze the image
def analyze_image(image_bytes: bytes, genai_model, image_url:str="") -> (str, str):
    """
    Analyze the image and return (categories, details).
    If an error occurs, return "error" as a category.
    """
    debug_details = {"initial_validation": None, "compression_attempts": [], "final_status": None}
    compressed_image_data = None
    max_compression_attempts = 2
    attempt = 0

    # Validate the initial image
    debug_details["initial_validation"] = "success" if validate_image(image_bytes) else "failed"

    # Try compressing the image
    while attempt < max_compression_attempts:
        try:
            compressed_image_data = compress_image(image_bytes)
            if compressed_image_data:
                if attempt != 1:
                    logger.info(f"Image compression succeeded on attempt {attempt + 1}.")
                debug_details["compression_attempts"].append(f"Success on attempt {attempt + 1}")
                break
        except Exception as e:
            logger.error(f"Image compression failed on attempt {attempt + 1}: {e}")
            debug_details["compression_attempts"].append(f"Failed on attempt {attempt + 1}: {e}")
        attempt += 1

    # If compression failed, attempt to redownload and compress again
    if not compressed_image_data:
        logger.warning("Image compression failed after multiple attempts. Redownloading image.")
        try:
            image_bytes = fetch_image(image_url)
            if validate_image(image_bytes):
                compressed_image_data = compress_image(image_bytes)
                if compressed_image_data:
                    logger.info("Image compression succeeded after redownload.")
                    debug_details["compression_attempts"].append("Success after redownload")
                else:
                    logger.error("Image compression failed after redownload.")
                    debug_details["compression_attempts"].append("Failed after redownload")
            else:
                logger.error("Redownloaded image is invalid.")
                debug_details["final_status"] = "Redownloaded image invalid"
                return "error", "Redownloaded image is invalid."
        except RuntimeError as e:
            debug_details["final_status"] = f"Image redownload failed: {e}"
            return "error", f"Image redownload failed: {e}"

    # If compression still failed, use original image bytes
    if not compressed_image_data:
        logger.warning("Proceeding with original image bytes after all compression attempts failed.")
        compressed_image_data = image_bytes
        debug_details["final_status"] = "Using original image bytes"


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

            details_str = analysis.get('details', 'No details provided.')

            # Prioritize categories
            # Step 1: Filter for pure H1/T1 combinations
            if set(categories).issubset({'H1', 'T1'}):  # Only H1, T1, or both
                if 'H1' in categories:
                    return 'H1', details_str  # Prioritize H1
                elif 'T1' in categories:
                    return 'T1', details_str
            else:
                # Step 2: If other categories exist, concatenate them with ', ' and return
                if categories:
                    return ', '.join(categories), details_str

            # Step 3: If no categories are present, return "good"
            return "good", details_str

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                return "error", f"Failed after {max_retries} retries: {e}"


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    import google.generativeai as genai

    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY", None)

    def configure_gemini(api_key: str):
        """Configure the generative AI model."""
        genai.configure(api_key=api_key)

        # Gemini model configuration
        model = genai.GenerativeModel('gemini-2.0-flash')

        return model

    # Configure Gemini with an API key
    genai_model  = configure_gemini(gemini_api_key)

    # response = genai_model.generate_content(contents=[ANALYSIS_PROMPT])
    #
    # print(response)

    # Load the image as bytes
    with open("Watermark present/img.png", "rb") as image_file:
        image_bytes = image_file.read()

    # Analyze the image using bytes
    categories, details = analyze_image(image_bytes, genai_model)
    logger.info(f"Categories: {categories}")
    logger.info(f"Details: {details}")

    print(categories)
    print(details)
