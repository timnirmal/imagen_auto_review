from fastapi import FastAPI, HTTPException
from analysis_utils import download_image, analyze_image
from supabase_utils import update_auto_review_results, get_images_with_status
from logging_config import logger
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI()

gemini_api_key = os.getenv("GEMINI_API_KEY", None)
if not gemini_api_key:
    raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

def configure_gemini(api_key: str):
    """Configure the generative AI model."""
    genai.configure(api_key=api_key)

    # Gemini model configuration
    model = genai.GenerativeModel('gemini-1.5-flash')

    return model

# Configure Gemini with an API key
genai_model  = configure_gemini(gemini_api_key)

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

BASE_URL = "https://cdn.midjourney.com"

def construct_image_url(job_id: str, image_index: int) -> str:
    """Construct the image URL from job_id and image_index."""
    return f"{BASE_URL}/{job_id}/0_{image_index}.png"

def validate_gemini_api_key(model):
    """Validate the Gemini API key by making a test request."""
    try:
        test_prompt = "Test API Key Validity"
        model.generate_content(contents=[test_prompt])
        logger.info("Gemini API key is valid.")
    except Exception as e:
        error_message = f"Gemini API key validation failed: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/auto_review/{job_id}/{image_index}")
def auto_review(job_id: str, image_index: int):
    """
    Retrieve the record from the database, construct the image URL, download and analyze the image,
    update the record with analysis results.
    """
    # Construct the image URL
    image_url = construct_image_url(job_id, image_index)
    print(f"Constructed Image URL: {image_url}")

    try:
        # 1. Download
        image_bytes = download_image(image_url)

        # Save the image to a file
        with open("image.png", "wb") as file:
            file.write(image_bytes)

        print("Image downloaded and saved as 'image.png'.")

        # 2. Analyze
        category_str, details_str = analyze_image(image_bytes, genai_model=genai_model)

        return {"message": "Auto review success", "categories": category_str, "details": details_str}

    except Exception as e:
        logger.exception("Error in auto_review endpoint")
        raise HTTPException(status_code=500, detail=str(e))


async def async_download_image(url: str) -> bytes:
    """Asynchronous wrapper for the pycurl-based download_image function."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, download_image, url)

async def process_record(record):
    """Download and process a single image."""
    try:
        # Construct the URL
        job_id = record["job_id"]
        image_index = record["image_index"]
        url = f"https://cdn.midjourney.com/{job_id}/0_{image_index}.jpeg"

        # Download the image
        image_bytes = await async_download_image(url)

        # Process the image (analyze it)
        category, details = analyze_image(image_bytes, genai_model=genai_model)

        # Update the database based on the analysis result
        if category == "error":
            update_auto_review_results(
                image_id=record["id"],
                auto_review_status="auto_review_error",
                review_status="auto_review_error",
                auto_review_details=details
            )
            return {"image_id": record["id"], "status": "error", "error": details}
        else:
            update_auto_review_results(
                image_id=record["id"],
                auto_review_status=category,
                review_status="auto_review_success",
                auto_review_details=details
            )
            return {"image_id": record["id"], "status": "success", "categories": category, "details": details}

    except Exception as e:
        # Handle errors and update the database with the error
        update_auto_review_results(
            image_id=record["id"],
            auto_review_status="auto_review_error",
            review_status="auto_review_error",
            auto_review_details=str(e)
        )
        return {"image_id": record["id"], "status": "error", "error": str(e)}


@app.post("/bulk_auto_review")
async def bulk_auto_review():
    # Validate the API key before starting bulk processing
    try:
        validate_gemini_api_key(genai_model)
    except HTTPException as e:
        return {"message": e.detail}

    """Process all images with review_status = 'added' in a single request."""
    images = get_images_with_status("added")
    if not images:
        return {"message": "No images found with review_status='added'."}

    print(images)

    # Process all images concurrently
    tasks = [process_record(record) for record in images]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {"message": "Bulk processing completed.", "results": results}
