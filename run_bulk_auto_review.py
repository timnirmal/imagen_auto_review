from fastapi.testclient import TestClient
from app import app
from tqdm import tqdm  # Import tqdm for progress bar
from datetime import datetime

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

def run_bulk_auto_review():
    response = client.post("/bulk_auto_review")
    return response.json()

if __name__ == "__main__":
    # end_time = datetime.strptime("7:50", "%H:%M").time()  # Define end time as 7:50 AM

    # for _ in tqdm(range(20), desc="Running bulk_auto_review"):
    with tqdm(desc="Running bulk_auto_review") as pbar:
        # while datetime.now().time() < end_time:  # Check if the current time is before 7:50 AM
        while True:  # Check if the current time is before 7:50 AM
            result = run_bulk_auto_review()
            print(result)  # Optionally print the result of each call
            pbar.update(1)
