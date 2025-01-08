# import requests
# from supabase_utils import supabase, logger
#
# def get_added_images():
#     """
#     Fetch all images that have review_status = 'added'.
#     """
#     response = supabase.table("midbot_images").select("*").eq("review_status", "added").execute()
#     return response.data

# def process_images():
#     base_url = "http://localhost:8000"  # or wherever your FastAPI is running
#     images = get_added_images()
#     logger.info(f"Found {len(images)} images with review_status='added'.")
#     for img in images:
#         image_id = img["id"]
#         endpoint = f"{base_url}/auto_review/{image_id}"
#         try:
#             resp = requests.post(endpoint, timeout=120)
#             if resp.status_code == 200:
#                 logger.info(f"Successfully auto-reviewed image {image_id}")
#             else:
#                 logger.error(f"Failed to auto-review image {image_id}, status={resp.status_code}, detail={resp.text}")
#         except Exception as e:
#             logger.exception(f"Exception while auto-reviewing image {image_id}")

# if __name__ == "__main__":
#     process_images()

# import pycurl
#
# url = "https://cdn.midjourney.com/c72a0374-f9b1-4a87-b383-452ee975345e/0_1.png"
# with open("imagesdssdsd.png", "wb") as f:
#     c = pycurl.Curl()
#     c.setopt(c.URL, url)
#     c.setopt(c.WRITEDATA, f)
#     c.setopt(c.HTTPHEADER, [
#         "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#         "accept-language: en-GB,en;q=0.9",
#         "priority: u=0, i",
#         "sec-ch-ua: \"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
#         "sec-ch-ua-mobile: ?0",
#         "sec-ch-ua-platform: \"Windows\"",
#         "sec-fetch-dest: document",
#         "sec-fetch-mode: navigate",
#         "sec-fetch-site: none",
#         "sec-fetch-user: ?1",
#         "upgrade-insecure-requests: 1",
#         "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#         "Referer: https://www.midjourney.com/"
#     ])
#     c.perform()
#     c.close()
