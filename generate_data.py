# generate_fake_data.py
from werkzeug.security import generate_password_hash
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from projekt import create_app, db
from projekt.models import User, Test
from datetime import datetime, timedelta
import random
from pathlib import Path
fake = Faker()

from faker.providers import DynamicProvider, BaseProvider


class SchoolSubjectsProvider(BaseProvider):
    def school_subject(self):
        subjects = [
            'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'History', 'Geography', 'Literature', 'Art',
            'Computer Science', 'Music', 'Physical Education',
            'Foreign Languages', 'Economics', 'Business Studies',
            'Psychology', 'Sociology', 'Philosophy', 'Health Education'
  
        ]
        return self.random_element(subjects)

names_provider=DynamicProvider(
     provider_name="names",
     elements= [
    "Summer Cup",
    "Winter Championship",
    "Spring Open",
    "Fall Masters",
    "Grand Slam",
    "Elite Invitational",
    "Pro League Finals",
    "Regional Showdown",
    "Global Clash",
    "Amateur Showcase",
],)

class ScientificTopicsProvider(BaseProvider):
    def scientific_topic(self):
        topics = [
            'Quantum Mechanics', 'General Relativity', 'Particle Physics',
            'String Theory', 'Cosmology', 'Astrophysics',
            'Nanotechnology', 'Biotechnology', 'Genetics', 'Neuroscience',
            'Climate Science', 'Environmental Science',
            'Mathematical Modeling', 'Data Science', 'Artificial Intelligence',
            'Robotics', 'Machine Learning', 'Cybersecurity',
            'Bioinformatics', 'Medicine', 'Health Sciences',
            'Chemical Engineering', 'Materials Science', 'Renewable Energy'
            # Add more scientific topics as needed
        ]
        return self.random_element(topics)
    
class LogoProvider(BaseProvider):
    def tournament_logos(self, num_logos=3):
        logos_path = Path("projekt/static")  # Update the path to your logos folder
        logos = list(logos_path.glob("*.png"))  # Assuming logos are in PNG format, adjust accordingly

        if len(logos) < num_logos:
            raise ValueError("Not enough logos available in the folder.")

        chosen_logos = random.sample(logos, num_logos)
        return [str(logo.relative_to(logos_path)) for logo in chosen_logos]
fake.add_provider(SchoolSubjectsProvider)
fake.add_provider(ScientificTopicsProvider)

fake.add_provider(LogoProvider)
app = create_app()
app.app_context().push()
def grades():
    p=['A', 'B','C','D','F']
    grades=[]
    for x in p:
        grade=(x, random.randint(0,10))
        grades.append(grade)
    return grades
def test():
    txt = f'{{"subject": "{fake.school_subject()}", "topic": "{fake.scientific_topic()}", "date": "{fake.date_time_this_year()}", "time": {random.randint(10,50)}, "max_points": {random.randint(5,50)}, "questions": [{{"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}}, {{"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}}, {{"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}}, {{"text": "Who was the President of the Confederate States of America during the American Civil War?", "points": 4, "type": "multiple-choice", "options": [["A", "Ulysses S. Grant"], ["B", "Robert E. Lee"], ["C", "Jefferson Davis"], ["D", "Abraham Lincoln"]], "correct_answer": "C"}}]}}'
    t=Test(
        creator_id=1,
        test=txt,
        is_graded=True,
        grades=str(grades())
    )
    return t
        
def populate_database():

    t=[User(
            email='123@gmail.com',
            password=generate_password_hash('123'),
            name=fake.first_name(),
            surname=fake.last_name(),
            confirmed=True,  
            confirmed_at=fake.date_time_this_year(),
        )]
    
    db.session.add_all(t)
    db.session.commit()

    t=[test() for x in range(5)]

    db.session.add_all(t)
    db.session.commit()
if __name__ == '__main__':
    populate_database()
    print("Fake data generated and added to the database.")
