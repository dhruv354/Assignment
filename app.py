from flask import Flask, request, jsonify, render_template
import csv
import uuid
import logging
import database
from tasks import process_images_task
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
database.init_db()

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_csv():
    logging.info("Received upload request")
    if 'file' not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    logging.info(f"File received: {file.filename}")
    if not file.filename.endswith('.csv'):
        logging.error("Invalid file type")
        return jsonify({"error": "Invalid file type"}), 400

    # Generate a unique request ID
    request_id = str(uuid.uuid4())

    # Parse CSV
    csv_data = []
    try:
        file_content = file.read().decode('utf-8')
        reader = csv.DictReader(file_content.splitlines())
        for row in reader:
            csv_data.append(row)
        logging.info(f"CSV data: {csv_data}")
    except UnicodeDecodeError:
        logging.error("Invalid file encoding")
        return jsonify({"error": "Invalid file encoding"}), 400
    except Exception as e:
        logging.error(f"Error parsing CSV: {e}")
        return jsonify({"error": f"Error parsing CSV: {str(e)}"}), 400

    # Validate CSV
    if not all('Serial Number' in row and 'Product Name' in row and 'Input Image Urls' in row for row in csv_data):
        logging.error("Missing required columns in CSV")
        return jsonify({"error": "Invalid CSV format"}), 400

    # Save request and CSV data to the database
    database.save_request(request_id, csv_data)

    # Trigger asynchronous image processing
    process_images_task.delay(request_id)

    logging.info(f"Request ID generated: {request_id}")
    return jsonify({"request_id": request_id}), 200

@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    status = database.get_request_status(request_id)
    if not status:
        return jsonify({"error": "Invalid request ID"}), 404
    return jsonify({"request_id": request_id, "status": status}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    request_id = data.get('request_id')
    status = data.get('status')
    if request_id and status:
        logging.info(f"Webhook received: Request {request_id} is {status}")
        return jsonify({"message": "Webhook received"}), 200
    return jsonify({"error": "Invalid webhook data"}), 400

if __name__ == '__main__':
    app.run(debug=True)