import cv2
import pytesseract
import numpy as np

# Path to the Tesseract OCR executable (change it to your specific installation path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract text from an image using PyTesseract OCR
def extract_text_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply additional image processing techniques to enhance clarity
    gray = cv2.medianBlur(gray, 5)  # Median blur to reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Gaussian blur to further reduce noise
    
    # Perform Canny edge detection
    edges = cv2.Canny(gray, 30, 100)
    
    # Find contours of the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask for the contours
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    
    # Bitwise-AND the mask with the gray image to extract the text region
    masked_image = cv2.bitwise_and(gray, gray, mask=mask)
    
    # Threshold the image to obtain a binary image with black text on a white background
    ret, thresholded = cv2.threshold(masked_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    text = pytesseract.image_to_string(thresholded)
    return text.strip()


# Path to the screen recording video file
video_path = "videos/video13.mp4"

# Read the screen recording video
video = cv2.VideoCapture(video_path)

# Capture the initial screenshot
ret, frame = video.read()
initial_screenshot = frame.copy()

# Get the dimensions of the screenshots
height, width, _ = initial_screenshot.shape

# Set the region of interest (ROI) coordinates for the follow button as a percentage of the screen size
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

# Set the region of interest (ROI) for the follow button in the initial and final screenshots
initial_roi = initial_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                                 int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]
final_roi = final_screenshot[int(roi_y * height / 100):int((roi_y + roi_height) * height / 100),
                             int(roi_x * width / 100):int((roi_x + roi_width) * width / 100)]

# Apply OCR to extract text from the region of interest in the initial and final screenshots
initial_text = extract_text_from_image(initial_roi)
final_text = extract_text_from_image(final_roi)


if "Subscribe" in initial_text and "Subscribed" in final_text:
    print("User subscribed on Youtube!")
elif "Subscribed" in initial_text and "Subscribe" in final_text:
    print("User unsubscribed on Youtube!")
else:
    print("No change in subscription status.")
