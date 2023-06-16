import cv2
import numpy as np

# Path to the screen recording video file
video_path = "videos/video20.mp4"

# Set the threshold for color change (adjust based on your needs)
color_change_threshold = 100

# Read the screen recording video
video = cv2.VideoCapture(video_path)

# Capture the initial and final screenshots
ret, frame = video.read()
if not ret:
    print("Failed to read the video.")
    exit()

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
# Draw a rectangle to indicate the region of interest in the initial and final screenshots
cv2.rectangle(initial_screenshot,
              (int(roi_x_percent / 100 * initial_screenshot.shape[1]), int(roi_y_percent / 100 * initial_screenshot.shape[0])),
              (int((roi_x_percent + roi_width_percent) / 100 * initial_screenshot.shape[1]), int((roi_y_percent + roi_height_percent) / 100 * initial_screenshot.shape[0])),
              (0, 255, 0), 2)

cv2.rectangle(final_screenshot,
              (int(roi_x_percent / 100 * final_screenshot.shape[1]), int(roi_y_percent / 100 * final_screenshot.shape[0])),
              (int((roi_x_percent + roi_width_percent) / 100 * final_screenshot.shape[1]), int((roi_y_percent + roi_height_percent) / 100 * final_screenshot.shape[0])),
              (0, 255, 0), 2)



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
    print("Failed to extract the region of interest.")
    exit()

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
    print("No change between initial and final screenshots.")
else:
    # Resize the initial screenshot, difference image, and binary image
    resize_scale = 0.5
    resized_initial = cv2.resize(initial_screenshot, None, fx=resize_scale, fy=resize_scale)
    resized_diff = cv2.resize(diff, None, fx=resize_scale, fy=resize_scale)
    resized_binary = cv2.resize(binary, None, fx=resize_scale, fy=resize_scale)

    # Convert the initial and final ROIs to grayscale
    initial_gray = cv2.cvtColor(initial_roi, cv2.COLOR_BGR2GRAY)
    final_gray = cv2.cvtColor(final_roi, cv2.COLOR_BGR2GRAY)

    # Calculate the mean pixel intensities of the grayscale ROIs
    initial_mean_intensity = np.mean(initial_gray)
    final_mean_intensity = np.mean(final_gray)

    # Check if the initial mean intensity is greater than the final mean intensity
    if initial_mean_intensity > final_mean_intensity:
        print("User unliked the video!")
    else:
        print("User liked the video!")
