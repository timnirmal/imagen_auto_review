# Image Auto-Review System

An automated image analysis system that processes images from an S3 bucket using Google's Gemini AI to detect various characteristics and updates review status in Supabase.

## Features

- Automated image analysis using Gemini AI
- Detection of multiple image characteristics:
  - Text content and spelling
  - Watermarks
  - Human presence
  - Nudity or inappropriate content
  - Blood/violence
  - Brand logos/trademarks
  - Copyright/movie content
  - Recognizable places
  - Recognizable people
- Image compression and validation
- Automatic retry mechanism
- Graceful shutdown handling
- Processing statistics tracking
- Multi-threaded image processing

## Category Codes

- `T1`: Text with correct spelling
- `T2`: Text with incorrect spelling
- `W1`: Watermark present
- `H1`: Contains humans
- `N1`: Contains nudity
- `B1`: Contains blood/violence
- `BR`: Contains brand logos
- `CP`: Copyright/movie content
- `PL`: Recognizable places
- `PP`: Recognizable people

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Setup

Create a `.env` file in the root directory with the following variables:

```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Usage

### Running the Auto-Review System

```bash
python app.py
```

### Running Bulk Auto-Review

```bash
python run_bulk_auto_review.py
```

## System Architecture

### Components

1. **analysis_utils.py**
   - Image downloading and validation
   - Image compression
   - AI analysis using Gemini
   - JSON response parsing

2. **app.py**
   - Main application logic
   - Image processing queue
   - Status updates to Supabase

3. **supabase_utils.py**
   - Database interaction
   - Status updates
   - Error handling

4. **logging_config.py**
   - Logging configuration
   - Error tracking

### Status Flow

1. **Initial State**: Image pending review
2. **Processing**: Image downloaded and analyzed
3. **Success States**:
   - `auto_review_success`: Image analyzed successfully
   - Categories assigned based on analysis
4. **Error States**:
   - `auto_review_error`: Processing failed

## Status Transitions Reference

### Process Record Function Transitions
- **Error Case**:
  - `auto_review_status` → `auto_review_error`
  - `review_status` → `auto_review_error`
- **Success Case**:
  - `auto_review_status` → [category result]
  - `review_status` → `auto_review_success`

### Fetch Images Processing Flow
- **Initial State**: `review_status` = `downloaded`
- **During Processing**: `review_status` → `processing`

### Additional Status Changes
- **Review Script**:
  - Checks for `review_status` = `added`
- **Rerun Process**:
  - Updates to:
    - `auto_review_status` = `good`
    - `review_status` = `rerun_for_clarity`

## Tools

### Image Categorizer (GUI)

Located in `Watermark present/1.0image-categorizer.py`
- GUI tool for manual image categorization
- Supports batch processing
- Category selection interface
- Progress tracking

### Image Sorter

Located in `Watermark present/1.1 automatic_before_image-sorter.py`
- Sorts processed images into category folders
- Handles duplicate filenames
- Category hierarchy implementation

## Error Handling

- Automatic retry mechanism for failed downloads
- Image validation before processing
- Graceful API key rotation
- Comprehensive error logging

## Performance Considerations

- Image compression to optimize processing
- Multi-threaded processing for better performance
- Rate limiting protection
- Memory usage optimization

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is proprietary and confidential. Unauthorized copying or distribution is prohibited.




## If key issue

```
{
  "message": "Gemini API key validation failed: 400 API key not valid. Please pass a valid API
  key. [reason: \"API_KEY_INVALID\"\ndomain: \"googleapis.com\"\nmetadata {\n  key: \"service\"\n  value: \"generativelanguage.googleapis.com\"\n}\n, locale: \"en-US\"\nmessage: \"API key not valid. Please pass a valid API key.\"\n]"
}
```

## Success Message

    {
      "message": "Bulk processing completed.",
      "results": [
        {
          "image_id": "3a1e331f-c1d3-47ce-a249-c6374967cb2a",
          "status": "success",
          "categories": "H1",
          "details": "The image shows a person's hands kneading a ball of dough on a wooden surface. The background is out of focus, showing a blurry view of a window with rain and city lights. There is no text, watermarks, brands, or recognizable people or places."
        },
        {
          "image_id": "e7e2614c-57d4-41db-bf7b-403445bf78a5",
          "status": "success",
          "categories": "H1",
          "details": "The image shows a person's hands kneading a ball of dough on a wooden surface. The background is blurry, showing what appears to be a window with out-of-focus lights and possibly rain or snow.  There is flour dust in the air.  No text, watermarks, brands, or recognizable individuals or locations are present."
        }
      ]
    }

1.

need a handling code

either run all the time or
we can create cron, every one hour - in our system we keep a timer, which will run for 45 mins after we start it.. and
afrer that when we recive Bulk processing completed. this stops...
after a process if we this message wasnt recived we need to get a notification to our system indicating that this is not
working

2.

make sure that we are try image for 3 times and after that we are ignoring and add it as error


GEMINI_API_KEY=AIzaSyDK9G2GPNURHTiMKLVbedzYoXi9j0pdoVk




025-01-13 01:33:49,441 [INFO] httpx - HTTP Request: POST http://testserver/bulk_auto_review "HTTP/1.1 200 OK"
Running bulk_auto_review:  90%|█████████ | 90/100 [6:06:58<1:49:54, 659.46s/it]{'message': 'Gemini API key validation failed: Timeout of 600.0s exceeded, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:74.125.130.95:443: tcp handshaker shutdown'}
2025-01-13 01:43:48,020 [ERROR] logging_config - Gemini API key validation failed: Timeout of 600.0s exceeded, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:74.125.24.95:443: tcp handshaker shutdown
2025-01-13 01:43:48,206 [INFO] httpx - HTTP Request: POST http://testserver/bulk_auto_review "HTTP/1.1 200 OK"
{'message': 'Gemini API key validation failed: Timeout of 600.0s exceeded, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:74.125.24.95:443: tcp handshaker shutdown'}
Running bulk_auto_review:  91%|█████████ | 91/100 [6:16:56<1:36:11, 641.25s/it]2025-01-13 01:53:45,361 [ERROR] logging_config - Gemini API key validation failed: Timeout of 600.0s exceeded, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:172.217.194.95:443: tcp handshaker shutdown
2025-01-13 01:53:45,678 [INFO] httpx - HTTP Request: POST http://testserver/bulk_auto_review "HTTP/1.1 200 OK"
{'message': 'Gemini API key validation failed: Timeout of 600.0s exceeded, last exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:172.217.194.95:443: tcp handshaker shutdown'}
Running bulk_auto_review:  92%|█████████▏| 92/100 [6:26:54<1:23:44, 628.12s/it]
Process finished with exit code -1