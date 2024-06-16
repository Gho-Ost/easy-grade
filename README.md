## Easy Grade

Easy grade is an application meant to support teachers in creating standardized tests and grading them effortlessly.

### Test creator
Test creator allows teachers to generate clean test sheet templates in pdf format.

Currently, 3 types of questions are supported:
- Short answer open questions
- "Fill the gaps" questions
- Multiple choice (A, B, C, D) questions

The test should be not larger than a single A4 page.

### Automatic grading
Utilizing the predefined structure of the test, automatic grading becomes very simple.

#### All you have to do is:
1. Select the test
2. Upload photographs of students' results
3. Run the grading process

Currently, automatic grading of multiple-choice questions is supported (not cheat proof).

#### Additional accessibility feature: High contrast mode

## App potential:
- AI supported question generation/modification
- Improved visual design
- Clearer visual information
- Improved grading system:
    - Prevent cheating
    - Grade open and fill the gaps questions: AI supported character reading, NLP comparison to expected answer
    - Allow for answer corrections
- Improved test statistics


### Running the application:
1. Run ```$env:FLASK_APP = "projekt"``` in powershell.
2. Run ```$env:FLASK_DEBUG = 1``` in powershell.
3. Make sure all package requirements are met. 
4. Run ```flask run```.
5. Navigate to the appropriate address in your browser.


---

Created for the Ultimate Hackathon Mission 3.0 organized by the AMU.
