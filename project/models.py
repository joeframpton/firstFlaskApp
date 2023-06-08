from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from .extensions import db, login_manager

class Admin(UserMixin, db.Model):
    name = db.Column(db.String(64), nullable=False)
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), nullable=False, unique = True)
    hashed_password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'Admin ("{self.email}" registered)'

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        self.hashed_password=generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)

    @login_manager.user_loader
    def load_user(email):
        return  Admin.query.get(email) 

class Biog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    area = db.Column(db.String(32), nullable=False)
    blurb = db.Column(db.Text, nullable=False)
    github = db.Column(db.String(32))
    linkedin = db.Column(db.String(32))
    twitter = db.Column(db.String(32))
    image_filename = db.Column(db.String(64))
    #mediumblob not in db.x 
    image_data = db.Column(MEDIUMBLOB)
    image_mimetype = db.Column(db.String(32))
    cv_filename = db.Column(db.String(64))
    cv_data = db.Column(MEDIUMBLOB)
    active = db.Column(db.Boolean, unique=True)
    work = db.relationship('Work', backref='biog', lazy=True)
    skills = db.relationship('Skills', backref='biog', lazy=True)
    contact = db.relationship('Contact', backref='biog', lazy=True)

    def __repr__(self):
        return f'{self.name} of {self.area}: {self.blurb}'
    
    #The following is adapted from the flask documentation https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
    ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg'}
    ALLOWED_EXTENSIONS_CV = {'pdf'}

    def allowed_file_img(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Biog.ALLOWED_EXTENSIONS_IMG

    def allowed_file_cv(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Biog.ALLOWED_EXTENSIONS_CV


class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date)
    job_description = db.Column(db.Text, nullable=False)
    biog_id = db.Column(db.Integer, db.ForeignKey('biog.id'), nullable=False)

    def __repr__(self):
        return f'{self.title} at {self.company}'

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(64), nullable=False)
    skill_description = db.Column(db.Text, nullable=False)
    biog_id = db.Column(db.Integer, db.ForeignKey('biog.id'), nullable=False)

    def __repr__(self):
        return f'{self.skill} registered'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    organisation = db.Column(db.String(64), default = None)
    email = db.Column(db.String(64), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    biog_id = db.Column(db.Integer, db.ForeignKey('biog.id'), nullable=False)

    def __repr__(self):
        return f'{self.name} of {self.organisation}, contactable by {self.email}'