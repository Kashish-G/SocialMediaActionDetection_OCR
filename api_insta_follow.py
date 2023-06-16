import cv2
import pytesseract
import numpy as np
import requests
from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread

app = Flask(__name__)
video_queue = Queue()

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

@app.route('/receive-video', methods=['POST'])
def receive_video():
    video_data = request.json
    video = video_data.get('video')
    video_id = video_data.get('video_id')
    video_queue.put((video, video_id))
    process_video_result()
    return jsonify({'status': 'success', 'code': 200, 'message': 'Video received', 'data': {'received': 1, 'queue_position': video_queue.qsize(), 'video_id': video_id}}), 200


def process_video_result():
    if video_queue.empty():
        return jsonify({'status': 'error', 'code': 404, 'message': 'No video file found'}), 404

    video_path, video_id = video_queue.get()
    video = cv2.VideoCapture(video_path)

    # Capture the initial screenshot
    ret, frame = video.read()
    initial_screenshot = frame.copy()

    # Get the dimensions of the screenshots
    height, width, _ = initial_screenshot.shape

    # Set the region of interest (ROI) coordinates for the follow button as a percentage of the screen size
    roi_x = int(10 / width * 100)  # Convert to percentage
    roi_y = int(10 / height * 100)  # Convert to percentage
    roi_width = width  # Convert to percentage
    roi_height = height  # Convert to percentage

    # Loop over each frame in the video
    while video.isOpened():
        # Read the current frame
        ret, frame = video.read()

        # If the frame was not successfully read, break the loop
        if not ret:
            break

        # Capture the final screenshot
        final_screenshot = frame.copy()

        # Press 'q' to quit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video and close any open windows
    video.release()
    cv2.destroyAllWindows()

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
    if "Follow" in initial_text and "Following" in final_text:
        result = "User Followed"
        user_followed = 1
    elif "Following" in initial_text and "Follow" in final_text:
        result = "User Unfollowed"
        user_followed = 0
    else:
        result = "No change"
        user_followed = 0

    # Prepare the response data
    response_data = {'status': 'success', 'code': 200, 'message': result, 'data': {'userFollowed': user_followed, 'video_id': video_id}}

    # Make a POST request to the desired API endpoint with the response data
    api_endpoint = 'http://localhost:5000/video-result'  # Replace with your API endpoint
    response = requests.post(api_endpoint, json=response_data)
    print(response_data)

    if response.status_code == 200:
        return jsonify({'status': 'success', 'code': 200, 'message': 'Video result processed and sent to API'}), 200
    else:
        return jsonify({'status': 'error', 'code': response.status_code, 'message': 'Failed to send video result to API'}), response.status_code



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'code': 404, 'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'status': 'fail', 'code': 500, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
