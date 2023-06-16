import cv2
import pytesseract
import numpy as np
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/like-status', methods=['POST'])
def detect_like_status():
    if 'video' not in request.files:
        return jsonify({'status': 'fail', 'code': 404, 'message': 'No video file found'}), 404
    
    video_file = request.files['video']
    video_path = 'videos_from_api/insta_like_check.mp4'
    video_file.save(video_path)
    
    # Read the screen recording video
    video = cv2.VideoCapture(video_path)

    # Capture the initial screenshot
    ret, frame = video.read()
    initial_screenshot = frame.copy()

    # Get the dimensions of the screenshots
    height, width, _ = initial_screenshot.shape

    # Set the region of interest (ROI) coordinates for the like count as a percentage of the screen size
    roi_x = 0  # Convert to percentage
    roi_y = 0  # Convert to percentage
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

    # Set the region of interest (ROI) for the like count in the initial and final screenshots
    initial_roi = initial_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                                     int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]
    final_roi = final_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                                 int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]

    # Apply OCR to extract text from the region of interest in the initial and final screenshots
    initial_text = extract_text_from_image(initial_roi)
    final_text = extract_text_from_image(final_roi)

    # Extract the number from the matched text using regular expressions
    initial_match = re.search(r'and\s+([\d,]+)\s+others', initial_text, re.IGNORECASE)
    final_match = re.search(r'and\s+([\d,]+)\s+others', final_text, re.IGNORECASE)

    if initial_match and final_match:
        initial_likes_text = initial_match.group(1)
        final_likes_text = final_match.group(1)

        # Remove commas from the number string
        initial_likes_text = initial_likes_text.replace(',', '')
        final_likes_text = final_likes_text.replace(',', '')

        # Convert the text to a number
        try:
            initial_likes = int(initial_likes_text)
            final_likes = int(final_likes_text)

            if final_likes == initial_likes + 1:
                result = "User liked the post!"
                user_liked = 1
            elif final_likes == initial_likes - 1:
                result = "User unliked the post!"
                user_liked = 0
            else:
                result = "No change in like status."
                user_liked = 0
        except ValueError:
            result = "Couldn't convert the text to a number."
            user_liked = 0
    else:
        result = "Couldn't extract the number of likes."
        user_liked = 0

    return jsonify({'status': 'success', 'code': 200, 'message': result, 'data': {'userLiked': user_liked}}), 200

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'code': 404, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'status': 'fail', 'code': 500, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
