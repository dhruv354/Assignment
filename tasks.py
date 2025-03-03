from celery import Celery
import requests
import os
import cv2
import numpy as np
from urllib.parse import urlparse, unquote
import database
import time  # For timestamp-based uniqueness

app = Celery('tasks', broker='redis://localhost:6379/0')

# Ensure static folder exists
os.makedirs("static/compressed_images", exist_ok=True)

@app.task
def process_images_task(request_id):
    """Processes images by reducing quality without resizing and stores output URLs."""

    # Fetch CSV data from the database
    products = database.get_products_by_request(request_id)

    for product in products:
        input_urls = product['input_image_urls'].split(',')
        output_urls = []

        for url in input_urls:
            try:
                # Download image
                response = requests.get(url.strip(), stream=True)
                response.raise_for_status()

                # Convert response to numpy array
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                if img is None:
                    raise ValueError(f"Failed to decode image from URL: {url}")

                # Extract filename and ensure a valid extension
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                filename = unquote(filename)  # Decode URL encoding

                ext = os.path.splitext(filename)[-1].lower()
                base_name = os.path.splitext(filename)[0]

                if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                    ext = ".jpg"  # Default to JPG

                # Generate a unique output filename
                timestamp = int(time.time())  # Current time for uniqueness
                output_filename = f"{base_name}_compressed_{timestamp}{ext}"
                output_path = os.path.join("static", "compressed_images", output_filename)

                # Save compressed image (reduce quality only)
                if ext in [".jpg", ".jpeg"]:
                    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 50])
                elif ext == ".png":
                    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
                else:
                    cv2.imwrite(output_path, img)

                # Store public URL
                image_url = f"http://localhost:5000/static/compressed_images/{output_filename}"
                output_urls.append(image_url)

            except Exception as e:
                print(f"Error processing {url}: {e}")

        # Update database with output URLs
        try:
            database.update_product_output_urls(product['id'], ','.join(output_urls))
        except Exception as e:
            print(f"Database update failed for {product['id']}: {e}")

    # Mark request as completed
    database.update_request_status(request_id, 'completed')

    # Trigger webhook
    requests.post('http://localhost:5000/webhook', json={
        "request_id": request_id,
        "status": "completed"
    })
