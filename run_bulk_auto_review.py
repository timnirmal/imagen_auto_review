from fastapi.testclient import TestClient
from app import app
from tqdm import tqdm  # Import tqdm for progress bar

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

def run_bulk_auto_review():
    response = client.post("/bulk_auto_review")
    return response.json()

if __name__ == "__main__":
    for _ in tqdm(range(20), desc="Running bulk_auto_review"):
        result = run_bulk_auto_review()
        print(result)  # Optionally print the result of each call
