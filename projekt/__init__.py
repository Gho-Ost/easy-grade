from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail 
import os
from flask_session import Session

db = SQLAlchemy()
mail = Mail() 
def create_app():
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'projekt/uploads')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'easygradeteam@gmail.com'
    app.config['MAIL_PASSWORD'] = 'pxxg sqcu alec ejdc'
    app.config['MAIL_DEFAULT_SENDER'] = 'easygradeteam@gmail.com'
    app.config['SECURITY_PASSWORD_SALT']='dsdasfasqe442331wf234derhgf42'
    Session(app)
    db.init_app(app)
    mail.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    with app.app_context():
            db.create_all()
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

if __name__=='__main__':
     app=create_app()
     app.run(debug=True)
