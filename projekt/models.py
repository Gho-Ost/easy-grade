from . import db
from flask_login import UserMixin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    surname = db.Column(db.String(1000))
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime)
    created_tests = db.relationship('Test', back_populates='creator')
 
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator=db.relationship('User', back_populates='created_tests')
    test=db.Column(db.String(99999999999), nullable=False)
    is_graded = db.Column(db.Boolean, default=False, nullable=False)
    grades=db.Column(db.String(100))
    