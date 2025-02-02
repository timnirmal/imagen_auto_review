import os
from dotenv import load_dotenv
from supabase import create_client, Client
from logging_config import logger
from datetime import datetime, timezone

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
image_limit = int(os.getenv("LIMIT"))

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise EnvironmentError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_image_record_by_id(image_id: str):
    """Fetch a single image record by id."""
    logger.info(f"Fetching record by id: {image_id}")
    response = supabase.table("midbot_images").select("*").eq("id", image_id).execute()
    data = response.data
    if data:
        return data[0]
    return None


def get_images_with_status(status: str):
    """Fetch all images with the given review_status and update them to 'processing' with updated_at timestamp."""
    logger.info(f"Fetching images with review_status={status}")

    # Step 1: Fetch images with the given status
    response = supabase.table("midbot_images").select("*").order("created_at").limit(image_limit).eq("review_status", status).execute()
    images = response.data

    if not images:
        return []

    # Extract the IDs of the fetched images
    image_ids = [image["id"] for image in images]

    # Get the current time in UTC
    current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Step 2: Update the review_status to 'processing' and set updated_at timestamp
    update_response = supabase.table("midbot_images").update({
        "review_status": "processing",
        "updated_at": current_utc_time
    }).in_("id", image_ids).execute()

    # Extract updated images from the response
    updated_images = update_response.data

    logger.info(f"Updated {len(image_ids)} images to 'processing' status with updated_at={current_utc_time}.")
    return updated_images


def update_auto_review_results(image_id: str, auto_review_status: str, review_status: str, auto_review_details: str):
    """
    Update the midbot_images table with the auto review results.
    - auto_review_status: categories or "auto_review_error"
    - review_status: "auto_review_success" or "auto_review_error"
    - auto_review_details: details or error message
    """
    logger.info(f"Updating auto_review_status for {image_id} = {auto_review_status}")
    response = (
        supabase.table("midbot_images")
        .update({
            "auto_review_status": auto_review_status,
            "review_status": review_status,
            "auto_review_details": auto_review_details
        })
        .eq("id", image_id)
        .execute()
    )
    return response.data
