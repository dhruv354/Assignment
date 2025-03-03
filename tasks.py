from celery import Celery
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse, unquote
import database
from config import Config
import cv2
from urllib.parse import urlparse, unquote


app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_images_task(request_id):
    # Fetch CSV data from the database
    products = database.get_products_by_request(request_id)

    for product in products:
        input_urls = product['input_image_urls'].split(',')
        output_urls = []

        for url in input_urls:
            try:
                # Download image
                response = requests.get(url.strip())  # Removed stream=True
                response.raise_for_status()

                # Convert response to numpy array
                image_array = np.frombuffer(response.content, dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                if img is None:
                    raise ValueError(f"Failed to decode image from URL: {url}")

                # 🔹 Compress image by 50% (resize width & height by half)
                img_resized = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))

                # Extract filename and extension
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                filename = unquote(filename)  # Decode URL encoding

                # Ensure valid extension (fallback to .jpg)
                ext = os.path.splitext(filename)[-1] or ".jpg"
                output_filename = f"output_{filename}"

                # 🔹 Save compressed image
                cv2.imwrite(output_filename, img_resized, [cv2.IMWRITE_JPEG_QUALITY, 50])
                output_urls.append(output_filename)

            except Exception as e:
                print(f"Error processing {url}: {e}")

        # Update database with output URLs
        database.update_product_output_urls(product['id'], ','.join(output_urls))

    # Mark request as completed
    database.update_request_status(request_id, 'completed')

    # Trigger webhook
    requests.post('http://localhost:5000/webhook', json={
        "request_id": request_id,
        "status": "completed"
    })
