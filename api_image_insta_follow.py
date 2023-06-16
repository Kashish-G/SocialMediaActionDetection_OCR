import cv2
import pytesseract
import numpy as np
import requests
from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread

app = Flask(__name__)
image_queue = Queue()

# Path to the Tesseract OCR executable (change it to your specific installation path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract text from an image using PyTesseract OCR
def extract_text_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply additional image processing techniques to enhance clarity
    gray = cv2.medianBlur(gray, 3)  # Median blur to reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Gaussian blur to further reduce noise
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # Binarization
    text = pytesseract.image_to_string(gray)
    return text.strip()

# Function to process the image result
def process_image_result():
    while True:
        initial_path, final_path, task_id = image_queue.get()
        initial_screenshot = cv2.imread(initial_path)
        final_screenshot = cv2.imread(final_path)
        # Get the dimensions of the screenshots
        height, width, _ = initial_screenshot.shape

        # Set the region of interest (ROI) coordinates for the follow button as a percentage of the screen size
        roi_x = int(10 / width * 100)  # Convert to percentage
        roi_y = int(10 / height * 100)  # Convert to percentage
        roi_width = width  # Convert to percentage
        roi_height = height  # Convert to percentage

        # Set the region of interest (ROI) for the follow button in the initial and final screenshots
        initial_roi = initial_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                                         int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]
        final_roi = final_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                                     int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]

        # Apply OCR to extract text from the region of interest in the initial and final screenshots
        initial_text = extract_text_from_image(initial_roi)
        final_text = extract_text_from_image(final_roi)

        # Process the extracted text to consider only the following text
        initial_text = initial_text.split("Following", 1)[-1].strip()
        final_text = final_text.split("Following", 1)[-1].strip()

        # Check if the follow button text has changed from the initial to the final screenshot
        result = ""
        if "Follow" in initial_text and "Following" in final_text and "Following" not in initial_text:
            result = "User followed on Instagram!"
            user_followed = 1
        elif "Following" in initial_text and "Follow" in final_text and "Following" not in final_text:
            result = "User unfollowed on Instagram!"
            user_followed = 0
        else:
            result = "No change in follow status."
            user_followed = 0

        # Prepare the response data
        response_data = {'status': 'success', 'code': 200, 'message': result,
                         'data': {'userFollowed': user_followed, 'task_id': task_id}}

        # Make a POST request to the desired API endpoint with the response data
        api_endpoint = 'http://localhost:5000/task-result'  # Replace with your API endpoint
        response = requests.post(api_endpoint, json=response_data)
        print(response_data)

        if response.status_code == 200:
            print('Task result processed and sent to API')
        else:
            print('Failed to send task result to API')

        image_queue.task_done()

image_processing_thread = Thread(target=process_image_result)
image_processing_thread.start()

@app.route('/receive-image', methods=['POST'])
def receive_image():
    image_data = request.json
    initial = image_data.get('initial')
    final = image_data.get('final')
    task_id = image_data.get('task_id')
    image_queue.put((initial, final, task_id))
    print(f"Image added to queue. Queue position: {image_queue.qsize()}")
    
    return jsonify({'status': 'success', 'code': 200, 'message': 'Images received',
                    'data': {'received': 1, 'queue_position': image_queue.qsize(), 'task_id': task_id}}), 200

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'code': 404, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'status': 'fail', 'code': 500, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)