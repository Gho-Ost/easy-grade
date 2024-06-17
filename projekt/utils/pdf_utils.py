import json
import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader, simpleSplit

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from io import BytesIO

pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))

def generate_aruco_marker(marker_id, size=100):
    """Generate an ArUco marker and return it as a PIL Image."""
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
    return marker

def draw_marker_on_canvas(pdf_canvas, marker, position, size=20):
    """Draws the ArUco marker on the PDF canvas at the given position."""
    marker_img = cv2.imencode('.png', marker)[1].tobytes()
    image = ImageReader(BytesIO(marker_img))
    pdf_canvas.drawImage(image, position[0], position[1], width=size, height=size, mask='auto')

def create_test_pdf(test_json, output_filename):
    """
    Create a well-formatted PDF file from a JSON description of a test.
    Place ArUco markers at the top left and bottom right of the PDF.
    """
    buffer = BytesIO()
    test_data = json.loads(test_json)

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Generate ArUco markers
    marker_top_left = generate_aruco_marker(0, 100)
    marker_bottom_right = generate_aruco_marker(1, 100)
    marker_top_right = generate_aruco_marker(2, 100)
    marker_bottom_left = generate_aruco_marker(3, 100)

    # Draw ArUco markers on the canvas
    draw_marker_on_canvas(c, marker_top_left, (10, height - 40), size=30)
    draw_marker_on_canvas(c, marker_bottom_right, (width - 40, 10), size=30)
    draw_marker_on_canvas(c, marker_top_right, (width - 40, height - 40), size=30)
    draw_marker_on_canvas(c, marker_bottom_left, (10, 10), size=30)

    # Set up styles
    c.setFont("VeraBI", 14)
    c.drawString(60, height - 40, f"Subject: {test_data['subject']}")
    c.setFont("VeraBd", 22)
    c.drawString(60, height - 75, f"Topic: {test_data['topic']}")
    c.setFont("VeraBd", 12)
    c.drawString(width-200, height - 40, f"Date: {test_data['date']}")
    c.drawString(width-320, height - 115, f"Name and Surname: ___________________________")
    c.drawString(50, height - 105, f"Duration: {test_data['time']} minutes")
    c.drawString(50, height - 120, f"Total Points: {test_data['max_points']}")

    y_position = height - 160
    question_counter = 1
    margin_left = 50
    wrap_width = width - 100

    for question in test_data['questions']:
        question_type = question['type']
        question_text = question['text']
        points = question['points']

        c.setFont("Times-Bold", 14)

        if question_type == 'multiple-choice':
            wrapped_question_text = simpleSplit(f"Q{question_counter}: {question_text} [{points} points]", "Times-Bold", 14, wrap_width)
            for line in wrapped_question_text:
                c.drawString(margin_left, y_position, line)
                y_position -= 20

            options = dict(question.get('options', []))
            square_size = 10
            for char in ["A", "B", "C", "D"]:
                # Draw the square
                c.rect(margin_left + 20, y_position - square_size + 9, square_size, square_size, stroke=1, fill=0)
                c.setFont("Times-Roman", 12)
                option_text = options[char]
                # Draw the option text next to the square
                wrapped_option_text = simpleSplit(f"{option_text}", "Times-Roman", 12, wrap_width - 40)
                text_y_position = y_position
                for line in wrapped_option_text:
                    c.drawString(margin_left + 40, text_y_position, line)
                    text_y_position -= 15
                y_position -= (15 * len(wrapped_option_text)) + 5

        elif question_type == 'fill-gaps':
            c.setFont("Times-Bold", 14)
            c.drawString(margin_left, y_position, f"Q{question_counter}: Fill in the gaps [{points} points]")

            y_position -= 20
            c.setFont("Times-Roman", 12)
            wrapped_fill_gaps_text = simpleSplit(question_text.replace("_", "___________________"), "Times-Roman", 12, wrap_width)
            for line in wrapped_fill_gaps_text:
                c.drawString(margin_left + 20, y_position, line)
                y_position -= 15

        elif question_type == 'short':
            wrapped_question_text = simpleSplit(f"Q{question_counter}: {question_text} [{points} points]", "Times-Bold", 14, wrap_width)
            for line in wrapped_question_text:
                c.drawString(margin_left, y_position, line)
                y_position -= 15

            y_position -= 10
            c.setFont("Times-Roman", 12)
            for _ in range(3):  # Add space for answer
                c.drawString(margin_left + 20, y_position, "___________________________________________________________________________")
                y_position -= 20

        question_counter += 1
        y_position -= 15

        # Check if we need a new page
        if y_position < 20:
            print("ERROR, test too large")
            print("Longer test support not implemented")
            return None

    c.save()
    buffer.seek(0)  # Rewind the buffer to the beginning
    return buffer

def json_to_closed_correct_positions(test_json, output_filename):
    """
    Create a well-formatted PDF file from a JSON description of a test.
    Place ArUco markers at the top left and bottom right of the PDF.
    """
    buffer = BytesIO()
    test_data = json.loads(test_json)

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Generate ArUco markers
    marker_top_left = generate_aruco_marker(0, 100)
    marker_bottom_right = generate_aruco_marker(1, 100)
    marker_top_right = generate_aruco_marker(2, 100)
    marker_bottom_left = generate_aruco_marker(3, 100)

    # Draw ArUco markers on the canvas
    draw_marker_on_canvas(c, marker_top_left, (10, height - 40), size=30)
    draw_marker_on_canvas(c, marker_bottom_right, (width - 40, 10), size=30)
    draw_marker_on_canvas(c, marker_top_right, (width - 40, height - 40), size=30)
    draw_marker_on_canvas(c, marker_bottom_left, (10, 10), size=30)

    # Set up styles
    c.setFont("VeraBI", 14)
    c.drawString(60, height - 40, f"Subject: {test_data['subject']}")
    c.setFont("VeraBd", 22)
    c.drawString(60, height - 75, f"Topic: {test_data['topic']}")
    c.setFont("VeraBd", 12)
    c.drawString(width-200, height - 40, f"Date: {test_data['date']}")
    c.drawString(width-320, height - 115, f"Name and Surname: ___________________________")
    c.drawString(50, height - 105, f"Duration: {test_data['time']} minutes")
    c.drawString(50, height - 120, f"Total Points: {test_data['max_points']}")

    y_position = height - 160
    question_counter = 1
    margin_left = 50
    wrap_width = width - 100

    positions = []
    for question in test_data['questions']:
        question_type = question['type']
        question_text = question['text']
        points = question['points']

        c.setFont("Times-Bold", 14)

        if question_type == 'multiple-choice':
            wrapped_question_text = simpleSplit(f"Q{question_counter}: {question_text} [{points} points]", "Times-Bold", 14, wrap_width)
            for line in wrapped_question_text:
                c.drawString(margin_left, y_position, line)
                y_position -= 20

            options = dict(question.get('options', []))
            square_size = 10
            for char in ["A", "B", "C", "D"]:
                # Draw the square
                if char == question["correct_answer"]:
                    positions.append(((margin_left + 20)/width, (y_position - square_size + 9)/height))
                
                c.rect(margin_left + 20, y_position - square_size + 9, square_size, square_size, stroke=1, fill=0)
                c.setFont("Times-Roman", 12)
                option_text = options[char]
                # Draw the option text next to the square
                wrapped_option_text = simpleSplit(f"{option_text}", "Times-Roman", 12, wrap_width - 40)
                text_y_position = y_position
                for line in wrapped_option_text:
                    c.drawString(margin_left + 40, text_y_position, line)
                    text_y_position -= 15
                y_position -= (15 * len(wrapped_option_text)) + 5

        elif question_type == 'fill-gaps':
            c.setFont("Times-Bold", 14)
            c.drawString(margin_left, y_position, f"Q{question_counter}: Fill in the gaps [{points} points]")

            y_position -= 20
            c.setFont("Times-Roman", 12)
            wrapped_fill_gaps_text = simpleSplit(question_text.replace("_", "___________________"), "Times-Roman", 12, wrap_width)
            for line in wrapped_fill_gaps_text:
                c.drawString(margin_left + 20, y_position, line)
                y_position -= 15

        elif question_type == 'short':
            wrapped_question_text = simpleSplit(f"Q{question_counter}: {question_text} [{points} points]", "Times-Bold", 14, wrap_width)
            for line in wrapped_question_text:
                c.drawString(margin_left, y_position, line)
                y_position -= 15

            y_position -= 10
            c.setFont("Times-Roman", 12)
            for _ in range(3):  # Add space for answer
                c.drawString(margin_left + 20, y_position, "___________________________________________________________________________")
                y_position -= 20

        question_counter += 1
        y_position -= 15

        # Check if we need a new page
        if y_position < 20:
            print("ERROR, test too large")
            print("Longer test support not implemented")
            return None

    return positions


# # Example JSON description of a test
# json_test = '{"subject": "History25", "topic": "The American Civil War", "date": "2024-06-19", "time": "45", "max_points": 39, "questions": [{"text": "Explain the main economic and social differences between the Northern and Southern states that contributed to the outbreak of the American Civil War.", "points": 10, "type": "short"}, {"text": "Describe the significance of the Emancipation Proclamation and its impact on the course of the Civil War.", "points": 6, "type": "short"}, {"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}, {"text": "Which battle is considered the turning point of the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Battle of Antietam"], ["B", "Battle of Gettysburg"], ["C", "Battle of Bull Run"], ["D", "Battle of Fort Sumter"]], "correct_answer": "B"}, {"text": "The American Civil War began in April _, when Confederate forces attacked Fort _ in South Carolina.", "points": 7, "type": "fill-gaps", "answers": ["1861", "Sumter"]}, {"text": "The final major battle of the Civil War took place at _ Court House in April _, leading to General Lee\'s surrender.", "points": 8, "type": "fill-gaps", "answers": ["Appomattox", "1865"]}]}'

# Generate the PDF
# print(json_to_closed_correct_positions(json_test, "test_example.pdf"))
