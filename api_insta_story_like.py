import cv2
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set the threshold for color change (adjust based on your needs)
color_change_threshold = 100

@app.route('/story-like-status', methods=['POST'])
def detect_like_status():
    if 'video' not in request.files:
        return jsonify({'status': 'fail', 'code': 404, 'message': 'No video file found'}), 404
    
    video_file = request.files['video']
    video_path = 'videos_from_api/insta_story_like_check.mp4'
    video_file.save(video_path)
    
    # Read the screen recording video
    video = cv2.VideoCapture(video_path)

    # Capture the initial and final screenshots
    ret, frame = video.read()
    if not ret:
        return jsonify({'status': 'fail', 'code': 500, 'message': 'Failed to read the video.'}), 500

    initial_screenshot = frame.copy()

    # Get the dimensions of the screenshots
    height, width, _ = initial_screenshot.shape

    # Set the region of interest (ROI) coordinates for the like button
    roi_x_percent = 70
    roi_y_percent = 85
    roi_width_percent = 20
    roi_height_percent = 10

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        final_screenshot = frame.copy()

    # Release the video
    video.release()

    # Set the region of interest (ROI) for the like button in the initial and final screenshots
    initial_roi = initial_screenshot[
                  int(roi_y_percent / 100 * initial_screenshot.shape[0]):
                  int((roi_y_percent + roi_height_percent) / 100 * initial_screenshot.shape[0]),
                  int(roi_x_percent / 100 * initial_screenshot.shape[1]):
                  int((roi_x_percent + roi_width_percent) / 100 * initial_screenshot.shape[1])
                  ]

    final_roi = final_screenshot[
                int(roi_y_percent / 100 * final_screenshot.shape[0]):
                int((roi_y_percent + roi_height_percent) / 100 * final_screenshot.shape[0]),
                int(roi_x_percent / 100 * final_screenshot.shape[1]):
                int((roi_x_percent + roi_width_percent) / 100 * final_screenshot.shape[1])
                ]

    # Check if the initial and final ROIs are valid
    if initial_roi.size == 0 or final_roi.size == 0:
        return jsonify({'status': 'fail', 'code': 500, 'message': 'Failed to extract the region of interest.'}), 500

    # Calculate the absolute difference between the initial and final ROIs
    diff = cv2.absdiff(initial_roi, final_roi)

    # Convert the difference to grayscale
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(gray, color_change_threshold, 255, cv2.THRESH_BINARY)

    # Count the number of nonzero pixels in the binary image
    pixel_count = cv2.countNonZero(binary)

    # Check if the pixel count is below the threshold
    no_change_threshold = 100  # Adjust this threshold based on your needs
    if pixel_count < no_change_threshold:
        result = "No change"
        user_liked = 0
        return jsonify({'status': 'success', 'code': 200, 'message': result, 'data': {'userLiked': user_liked}}), 200


    else:
        # Convert the initial and final ROIs to grayscale
        initial_gray = cv2.cvtColor(initial_roi, cv2.COLOR_BGR2GRAY)
        final_gray = cv2.cvtColor(final_roi, cv2.COLOR_BGR2GRAY)

        # Calculate the mean pixel intensities of the grayscale ROIs
        initial_mean_intensity = np.mean(initial_gray)
        final_mean_intensity = np.mean(final_gray)

        # Check if the initial mean intensity is greater than the final mean intensity
        if initial_mean_intensity > final_mean_intensity:
            result = "User unliked the story!"
            user_liked = 0
        else:
            result = "User liked the story!"
            user_liked = 1

        return jsonify({'status': 'success', 'code': 200, 'message': result, 'data': {'userLiked': user_liked}}), 200



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'status': 'error', 'code': 404, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'status': 'error', 'code': 500, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
