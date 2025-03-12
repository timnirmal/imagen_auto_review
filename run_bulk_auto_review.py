from fastapi.testclient import TestClient
from app import app
from tqdm import tqdm
from datetime import datetime, timedelta
import time
import keyboard
import signal
import sys

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

# Global flag to track if termination is requested
termination_requested = False

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    global termination_requested
    if not termination_requested:
        print("\nGraceful termination requested. Completing current batch before exiting...")
        termination_requested = True
    else:
        print("\nForced exit. Terminating immediately.")
        sys.exit(0)

def run_bulk_auto_review():
    """Run a single batch of auto review"""
    response = client.post("/bulk_auto_review")
    return response.json()

def print_summary(success_count, error_count, start_time):
    """Print a summary of the processing statistics"""
    total_count = success_count + error_count
    elapsed_time = time.time() - start_time
    elapsed_formatted = str(timedelta(seconds=int(elapsed_time)))
    
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    print(f"Total images processed: {total_count}")
    print(f"Successful: {success_count} ({success_count/total_count*100:.1f}% of total)" if total_count > 0 else "Successful: 0 (0.0% of total)")
    print(f"Failed: {error_count} ({error_count/total_count*100:.1f}% of total)" if total_count > 0 else "Failed: 0 (0.0% of total)")
    print(f"Time elapsed: {elapsed_formatted}")
    print(f"Average processing time: {elapsed_time/total_count:.2f} seconds per image" if total_count > 0 else "Average processing time: N/A")
    print("=" * 50)

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize counters and timer
    success_count = 0
    error_count = 0
    start_time = time.time()
    batch_count = 0
    
    print("Starting bulk auto review process. Press Ctrl+C to gracefully terminate.")
    
    with tqdm(desc="Running bulk_auto_review") as pbar:
        while not termination_requested:
            # Run a batch of auto review
            result = run_bulk_auto_review()
            batch_count += 1
            
            # Process results and update statistics
            if "results" in result:
                for item in result["results"]:
                    if isinstance(item, dict) and "status" in item:
                        if item["status"] == "success":
                            success_count += 1
                        else:  # status is "error"
                            error_count += 1
            
            # Update progress bar
            pbar.update(1)
            
            # Check if user pressed 'q' to quit
            if keyboard.is_pressed('q'):
                print("\nGraceful termination requested. Completing current batch before exiting...")
                termination_requested = True
    
    # Print final summary
    print_summary(success_count, error_count, start_time)
    print(f"Total batches processed: {batch_count}")
    print("Bulk auto review process completed.")
