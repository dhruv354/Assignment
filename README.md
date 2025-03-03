# Image Processing Service

## Overview
This project is a Flask-based web service that allows users to upload a CSV file containing product details and image URLs. The images are processed using Celery and OpenCV, reducing the image quality by 50%.

## Features
- CSV Upload for bulk image processing.
- Background processing using Celery.
- Image quality compression.
- Webhooks for status updates.
- SQLite database for tracking requests and images.

## Tech Stack
- **Backend:** Flask
- **Task Queue:** Celery
- **Message Broker:** Redis
- **Database:** SQLite


## Running the Project

### 1. Start Redis Server
```sh
redis-server
```

### 2. Start Celery Worker
```sh
celery -A tasks worker --loglevel=info
```

### 3. Start Flask App
```sh
python app.py
```

## API Endpoints

### Upload CSV
```
POST /upload
```
- **Description:** Uploads a CSV file containing image URLs.
- **Request:** Multipart form-data (`file` as CSV)
- **Response:** JSON with `request_id`

### Check Request Status
```
GET /status/<request_id>
```
- **Description:** Checks the processing status of an uploaded CSV.
- **Response:** JSON with `status`

### Webhook (Triggered after processing)
```
POST /webhook
```
- **Description:** Notifies when processing is completed.
- **Payload:** `{ "request_id": "<id>", "status": "completed" }`

## How Image Processing Works

1. **User uploads CSV:**
   - Contains serial number, product name, and image URLs.
2. **Flask saves the request:**
   - Stores request info in SQLite and triggers Celery task.
3. **Celery downloads & processes images:**
   - Downloads the image.
   - Reduces quality by 50%.
   - Saves in `static/compressed_images/`.
4. **Database is updated:**
   - Stores processed image URLs.
5. **Webhook is triggered:**
   - Sends completion status to an endpoint.

## Example CSV File
```csv
Serial Number,Product Name,Input Image Urls
1,SKU1,https://example.com/image1.jpg
2,SKU2,https://example.com/image2.png
```

