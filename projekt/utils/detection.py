import cv2
import numpy as np
import random
from .pdf_utils import json_to_closed_correct_positions
import json

def detect_marker(img_path):
    image = cv2.imread(img_path)

    # Load the dictionary that was used to generate the markers.
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    # Initialize the detector parameters using default values.
    parameters = cv2.aruco.DetectorParameters()
    detector=cv2.aruco.ArucoDetector(aruco_dict, parameters)
    # Detect the markers in the image.
    corners, ids, rejectedImgPoints = detector.detectMarkers(image)

    # Draw the detected markers on the image.
    detected_markers = cv2.aruco.drawDetectedMarkers(image.copy(), corners, ids)
   
    # Display the image with detected markers.
    return corners, image


def order_points(pts):
    # Initializing a list of coordinates that will be ordered
    # such that the first entry is the top-left, the second is the top-right,
    # the third is the bottom-right, and the fourth is the bottom-left.
    rect = np.zeros((4, 2), dtype="float32")

    # The top-left point will have the smallest sum, whereas the
    # bottom-right point will have the largest sum.
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # The top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference.
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def transform(corners, image):
    if len(corners) == 4:
        # Flatten the corners array.
        corners = [corner[0] for corner in corners]
        
        # Order the corners.
        ordered_corners = order_points(np.concatenate(corners))
        
        # Determine the width and height of the new image.
        (tl, tr, br, bl) = ordered_corners
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))
        
        # Set up destination points to get a "birds-eye view".
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        # Compute the perspective transform matrix.
        M = cv2.getPerspectiveTransform(ordered_corners, dst)
        
        # Apply the perspective transformation to get the warped image.
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        # Display the warped image.
        cv2.imwrite('projekt/uploads/transform3.png', warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return warped
    else:
        print("Could not detect exactly four ArUco markers.")

def get_closed_test_results(img_path, positions):
    # cv2.resize(roi, (roi.shape[1]//4, roi.shape[0]//4))
    # cv2.imshow('win', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    calibrated_test = transform(*detect_marker(img_path))
    # gray = cv2.cvtColor(calibrated_test, cv2.COLOR_BGR2GRAY)

    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([255, 255, 255])

    hsv = cv2.cvtColor(calibrated_test, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=4)

    results = []
    for p in positions:
        empty = np.zeros_like(opening)
        cv2.circle(empty, (int(p[0]*opening.shape[1]), opening.shape[0] - int(p[1]*opening.shape[0])),
                    radius=30, color=(255, 255, 255), thickness=-1)  # BGR color format
        
        results.append(np.any(np.where(empty * opening == 1, 1, 0)))

    return results

def check_answers(img_path, json_test):
    positions = json_to_closed_correct_positions(json_test, "")
    closed_results = get_closed_test_results(img_path, positions)

    json_test = json.loads(json_test)
    j = 0
    results = []
    for i, question in enumerate(json_test["questions"], start=1):
        if question['type'] == 'multiple-choice':
            if closed_results[j]:
                results.append((i, question['points']))

            else:
                results.append((i, 0))

            j += 1
        else:
            results.append((i, random.randint(0, question['points'])))

    return results

# json_test = '{"subject": "History25", "topic": "The American Civil War", "date": "2024-06-19", "time": "45", "max_points": 39, "questions": [{"text": "Explain the main economic and social differences between the Northern and Southern states that contributed to the outbreak of the American Civil War.", "points": 10, "type": "short"}, {"text": "Describe the significance of the Emancipation Proclamation and its impact on the course of the Civil War.", "points": 6, "type": "short"}, {"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}, {"text": "Which battle is considered the turning point of the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Battle of Antietam"], ["B", "Battle of Gettysburg"], ["C", "Battle of Bull Run"], ["D", "Battle of Fort Sumter"]], "correct_answer": "B"}, {"text": "The American Civil War began in April _, when Confederate forces attacked Fort _ in South Carolina.", "points": 7, "type": "fill-gaps", "answers": ["1861", "Sumter"]}, {"text": "The final major battle of the Civil War took place at _ Court House in April _, leading to General Lee\'s surrender.", "points": 8, "type": "fill-gaps", "answers": ["Appomattox", "1865"]}]}'
# print(check_answers("projekt/uploads/img1.jpg", json_test))