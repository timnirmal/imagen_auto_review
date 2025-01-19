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