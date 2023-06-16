import cv2
import pytesseract
import numpy as np
import queue

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

# Define a queue to store the requests
request_queue = queue.Queue()

# Function to process a single request from the queue
def process_request(request):
    # Get the request data
    initial_screenshot, final_screenshot = request

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
    elif "Following" in initial_text and "Follow" in final_text and "Following" not in final_text:
        result = "User unfollowed on Instagram!"
    else:
        result = "No change in follow status."

    # Print the result
    print(result)

# Path to the initial and final screenshot files
initial_screenshot_path = "screenshots/img2.jpg"
final_screenshot_path = "screenshots/img1.jpg"

# Read the initial and final screenshots
initial_screenshot = cv2.imread(initial_screenshot_path)
final_screenshot = cv2.imread(final_screenshot_path)

# Add the request to the queue
request_queue.put((initial_screenshot, final_screenshot))

# Process the requests in the queue
while not request_queue.empty():
    request = request_queue.get()
    process_request(request)
