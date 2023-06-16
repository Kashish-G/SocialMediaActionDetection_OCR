import cv2
import numpy as np

# Path to the screen recording video file
video_path = "videos/video28.mp4"

# Set the threshold for color change (adjust based on your needs)
color_change_threshold = 50

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
roi_x_percent = 80
roi_y_percent = 55
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

# Convert the initial and final ROIs to grayscale
initial_gray = cv2.cvtColor(initial_roi, cv2.COLOR_BGR2GRAY)
final_gray = cv2.cvtColor(final_roi, cv2.COLOR_BGR2GRAY)

# Calculate the optical flow between initial and final ROIs
optical_flow = cv2.calcOpticalFlowFarneback(initial_gray, final_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

# Calculate the magnitudes of optical flow vectors
flow_magnitudes = np.sqrt(np.square(optical_flow[..., 0]) + np.square(optical_flow[..., 1]))

# Threshold the flow magnitudes to identify significant movements
significant_movements = flow_magnitudes > color_change_threshold

# Count the number of significant movements
pixel_count = np.count_nonzero(significant_movements)

# Calculate the mean pixel intensities of the grayscale ROIs
initial_mean_intensity = np.mean(initial_gray)
final_mean_intensity = np.mean(final_gray)

# Calculate the intensity difference between initial and final ROIs
intensity_diff = abs(final_mean_intensity - initial_mean_intensity)

# Calculate the percentage of red pixels in the initial and final ROIs
initial_red_pixels = np.count_nonzero(initial_roi[:, :, 2] > 200)  # Assuming red pixels have high R channel values
final_red_pixels = np.count_nonzero(final_roi[:, :, 2] > 200)

initial_roi_area = initial_roi.shape[0] * initial_roi.shape[1]
final_roi_area = final_roi.shape[0] * final_roi.shape[1]

initial_red_percentage = initial_red_pixels / initial_roi_area * 100
final_red_percentage = final_red_pixels / final_roi_area * 100



# Define the thresholds for pixel count, intensity difference, and red percentage
threshold_low = 100
threshold_high = 1000
intensity_diff_threshold = 1
red_percentage_threshold = 1  # Adjust this threshold as needed

# Calculate the difference in red percentages
red_percentage_diff = final_red_percentage - initial_red_percentage

# If there are significant movements and the intensity difference is above the threshold, and the final red percentage is higher than initial, the user liked the reel
if initial_red_percentage < final_red_percentage:
    print("User liked the reel!")
# If the initial red percentage is higher than the final red percentage, the user unliked the reel
elif initial_red_percentage > final_red_percentage:
    if intensity_diff>5:
        print("User unliked the reel!")
# Otherwise, the user did not like the reel
    else:
        print("No change")
