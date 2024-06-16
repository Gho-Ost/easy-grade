from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, current_app, session, jsonify, send_file, send_from_directory
from flask_login import login_required, current_user
from . import db
from .models import Test, User
from datetime import datetime
import requests
from werkzeug.utils import secure_filename
from .utils.decorators import check_is_confirmed
from .utils.pdf_utils import create_test_pdf
from .utils.detection import check_answers
from itertools import combinations
import random
import math
import os
import json

main = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
@main.route('/')
def index():
  
    
  
    return render_template('index.html')
 

@main.route('/profile')
@login_required
@check_is_confirmed
def profile():
    # Tournaments created by the user
    created_tests = Test.query.filter_by(creator_id=current_user.id, is_graded=False).all()
    c_test=clean_test(created_tests, sep=True)

    # Tournaments in which the user participates
    graded_tests =  Test.query.filter_by(creator_id=current_user.id, is_graded=True).all()
    g_test=clean_test(graded_tests, sep=True)
    grades=[]
    for x in graded_tests:
        p=x.grades
        if p is None:
            p=str([('A', 0),('B', 0),('C', 0),('D', 0),('F', 0)])
        grades.append(eval(p))
    print(grades)
    return render_template('profile.html', name=current_user.name, created_tests=c_test, graded_tests=g_test, grades=grades)



@main.route('/create_test')
@login_required
@check_is_confirmed
def create_test():

    return render_template('create_test.html')

@main.route('/save_test', methods=['POST'])
@login_required
@check_is_confirmed
def save_test():
    # Extract form data
    subject = request.form['subject']
    topic = request.form['topic']
    date = request.form['date']
    time = request.form['time']
    question_types = dict([(int(key.split(",")[1]), value) for key, value in request.form.items() if key.startswith("question") and key.split(",")[2] == "type"])
    
    # Initialize a list to hold questions
    max_points = 0
    questions = []
    for key, value in request.form.items():
        
        if key.startswith('questions'):
            # Example key: questions,1,text
            # Split the key into its components
            parts = key.split(',')
            index = int(parts[1])


            field = parts[2]

            # Append question if missing space
            if len(questions) <= index:
                question = None
                if question_types[index] == "short":
                    question = {'text': '', 'points': 0, 'type': 'short'}
                elif question_types[index] == "multiple-choice":
                    question = {'text': '', 'points': 0, 'type': 'multiple-choice', 'options': [], 'correct_answer': ''}
                elif question_types[index] == "fill-gaps":
                    question = {'text': '', 'points': 0, 'type': 'fill-gaps', 'answers': ''}
                questions.append(question)
            if field == 'text':
                questions[index]['text'] = value
            elif field == 'points':
                max_points += int(value)
                questions[index]['points'] = int(value)
            elif field == 'optionsA':
                questions[index]['options'].append(("A", value))
            elif field == 'optionsB':
                questions[index]['options'].append(("B", value))
            elif field == 'optionsC':
                questions[index]['options'].append(("C", value))
            elif field == 'optionsD':
                questions[index]['options'].append(("D", value))
            elif field == 'correct_answer':
                questions[index]['correct_answer'] = value
            elif field == 'answers':
                questions[index]['answers'] = value.split(',')
    test_json = json.dumps({
        'subject': subject,
        'topic': topic,
        'date': date,
        'time': time,
        'max_points': max_points,
        'questions': questions
    })
    new_test = Test(
        creator_id = current_user.id,
        test = test_json
    )

    db.session.add(new_test)
    db.session.commit()
    # print(test_json)

    res = create_test_pdf(test_json, f"Easy Grade {subject} {date} Test.pdf")
    if res is None:
        flash("Test pdf creation failed. The test might be too long.", "danger")

        return render_template("create_test.html")
        
    else:
        return send_file(
            res,
            as_attachment=True,
            download_name=f"Easy Grade {subject} {date} Test.pdf",
            mimetype='application/pdf'
        )


@main.route('/grade_test', methods=['GET', 'POST'])
@login_required
@check_is_confirmed
def grade_test(): 
    user_tests = Test.query.filter_by(creator_id=current_user.id).all()
    tests_clean = clean_test(user_tests)
    return render_template('grade.html', name=current_user.name, tests=tests_clean)

def clean_test(tests, sep=False):
    tests_clean = []
    for tt in tests:
        t = json.loads(tt.test)
        subject = t.get('subject')
        topic = t.get('topic')
        date = t.get('date')
        id = tt.id
        if sep:
            tests_clean.append([id, subject, topic, date])
        else:
            tests_clean.append([id, f'{subject} {topic} {date}'])
    return tests_clean

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/upload', methods=['POST'])
@login_required
@check_is_confirmed
def upload():
    if 'files[]' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('main.grade_test'))

    files = request.files.getlist('files[]')

    if len(files) == 0:
        flash('No selected file', 'danger')
        return redirect(url_for('main.grade_test'))

    session_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid)
    os.makedirs(session_folder, exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(session_folder, filename)
            file.save(file_path)
        else:
            flash(f'File {file.filename} is of an incorrect type', 'danger')
            return redirect(url_for('main.grade_test'))
    
    flash('Files uploaded successfully', 'success')
    return redirect(url_for('main.grade_test'))
def process_grades(grades, test_id):
    test = Test.query.get(test_id)
    t=json.loads(test.test)
    max_points=t.get('max_points')
    p=0
    for points in grades:
        p+=points[1]
    grade=('F'*50+'D'*15+'C'*13+'B'*12+'A'*10)[int((p/max_points)*100)]
    p=test.grades
    if p is None:
        p=str([('A', 0),('B', 0),('C', 0),('D', 0),('F', 0)])
    test.grades=str([x if x[0]!=grade else (grade, x[1]+1) for x in eval(p) ])
    db.session.commit()
    return grade



@main.route('/grade_tests', methods=['POST', 'GET'])
@login_required
@check_is_confirmed
def grade_tests():
    test_id = request.form.get('test_id')
    if not test_id:
        flash("No test selected for grading.", "danger")
        return redirect(url_for('main.create_test'))
    test = Test.query.get(test_id)
    if not test:
        flash("Selected test not found.", "danger")
        return redirect(url_for('main.create_test'))
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid)
    if not os.path.exists(upload_folder):
        flash("No uploaded files found to grade.", "danger")
        return redirect(url_for('main.create_test'))
    test_json = json.loads(test.test)
    # Log the test name and graded results
    print(f"Grading Test: {test_json['topic']}")

    grades=[]
    for filename in os.listdir(upload_folder):
        if filename.endswith(('.jpg', '.png', '.pdf')):
            results = check_answers(os.path.join(upload_folder, filename), test.test)
        
            grades.append([process_grades(results, test_id),  filename, results])
            print("Results:", results)
    points=[]
    for q in test_json['questions']:
        points.append(q['points'])
    flash(f"Grading completed for test '{test_json['topic']}'.", "success")
    # Optionally, you could return these results in a template or redirect to a different page
    return render_template('results.html', results=grades, test=test_json, points=points)

@main.route('/files', methods=['GET'])
@login_required
@check_is_confirmed
def list_files():
    session_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid)
    if not os.path.exists(session_folder):
        return jsonify([])

    files = os.listdir(session_folder)
    file_urls = [url_for('main.download_file', filename=filename) for filename in files]
    return jsonify(file_urls)

@main.route('/delete_file/<filename>', methods=['DELETE'])
@login_required
@check_is_confirmed
def delete_file(filename):
    session_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid)
    file_path = os.path.join(session_folder, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@main.route('/download/<filename>')
@login_required
@check_is_confirmed
def download_file(filename):
    session_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid)
    return send_from_directory(session_folder, filename)


@main.route('/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], session.sid), filename)