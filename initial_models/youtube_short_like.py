import cv2
import numpy as np

# Path to the screen recording video file
video_path = "videos/video29.mp4"

# Set the threshold for color change (adjust based on your needs)
color_change_threshold = 25

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
roi_x_percent = 87
roi_y_percent = 42
roi_width_percent = 10
roi_height_percent = 5

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
    print("Failed to extract the region of interest.")
    exit()

# Convert the initial and final ROIs to grayscale
initial_gray = cv2.cvtColor(initial_roi, cv2.COLOR_BGR2GRAY)
final_gray = cv2.cvtColor(final_roi, cv2.COLOR_BGR2GRAY)

# Calculate the absolute difference between the initial and final ROIs
roi_diff = cv2.absdiff(initial_gray, final_gray)

# Apply a threshold to the difference image to identify significant movements
_, threshold = cv2.threshold(roi_diff, color_change_threshold, 255, cv2.THRESH_BINARY)

# Count the number of non-zero pixels in the thresholded image
pixel_count = cv2.countNonZero(threshold)

# Calculate the mean pixel intensities of the grayscale ROIs
initial_mean_intensity = np.mean(initial_gray)
final_mean_intensity = np.mean(final_gray)

# Calculate the intensity difference between initial and final ROIs
intensity_diff = abs(final_mean_intensity - initial_mean_intensity)

# Calculate the percentage of white pixels in the initial and final ROIs
initial_white_pixels = np.count_nonzero(initial_roi[:, :, 2] > 200)  # Assuming white pixels have high R channel values
final_white_pixels = np.count_nonzero(final_roi[:, :, 2] > 200)

initial_roi_area = initial_roi.shape[0] * initial_roi.shape[1]
final_roi_area = final_roi.shape[0] * final_roi.shape[1]

initial_white_percentage = initial_white_pixels / initial_roi_area * 100
final_white_percentage = final_white_pixels / final_roi_area * 100

# Define the thresholds for intensity difference and white percentage
intensity_diff_threshold = 50
white_percentage_threshold = 50  # Adjust this threshold as needed



# If there are significant movements and the intensity difference is above the threshold, and the final white percentage is higher than the initial, the user liked the reel
if pixel_count > 0 and intensity_diff > intensity_diff_threshold and final_white_percentage < initial_white_percentage:
    print("User liked the reel!")
# If the initial white percentage is higher than the final white percentage, the user unliked the reel
elif initial_white_percentage < final_white_percentage:
        print("User unliked the reel!")

# Display the initial and final screenshots with the ROI and area information
initial_screenshot_with_area = cv2.putText(initial_screenshot, f"Area: {initial_roi_area}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
final_screenshot_with_area = cv2.putText(final_screenshot, f"Area: {final_roi_area}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

