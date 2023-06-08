from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, EmailField, PasswordField, BooleanField, DateField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import InputRequired, Email, Length, ValidationError, Regexp, EqualTo, Optional
from .models import Admin, Biog

class AdminRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="Please enter your name") , Length(max=64, message="Please enter something shorter")])
    email = EmailField('Email', validators=[Email(message='Please enter a valid email'), InputRequired(message="Please enter your email"), Length(max=64, message="Please enter something shorter")]) 
    password = PasswordField('Password', validators=[InputRequired(message="Please enter a password"), Length(min=10, message="Your password must contain letters and number and be at least 10 characters long"), EqualTo('confirm_password', message="Your password confirmation must be the same"), Regexp('^(?=.*\d)(?=.*[A-Za-z])(?=.*[a-zA-Z]).{10,}$', message= "Your password must contain letters and number and be at least 10 characters long")])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(message="Please confirm your password"), Length(min=10,message="Your password must contain letters and number and be at least 10 characters long")]) 
    submit = SubmitField('Add')
    #password regex from https://regexr.com/3bfsi

    def validate_user(self, email):
        email = Admin.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('That email address is already registered')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Please enter a valid email address"), InputRequired(message="Please enter your email")])
    password = PasswordField('Password', validators=[InputRequired(message="Please enter your password")])
    remember_me = BooleanField('Remember Me', default=False)
    submit = SubmitField('Login')

class WorkForm(FlaskForm):
    biog_id = SelectField('Which user is this for?', validators=[InputRequired(message="Please select a person")])
    title = StringField('Job Title', validators=[InputRequired(message="Please enter a job title"), Length(max=64, message="Please enter a shorter job title")])
    company = StringField('Company Name', validators=[InputRequired(message="Please enter a company name"), Length(max=64, message="Please enter a shorter company name")])
    start = DateField('Start Date', validators=[InputRequired(message="Please enter a start date")])
    end = DateField('End Date', validators=[Optional()])
    job_description = TextAreaField('Summary of the role', validators=[InputRequired(message="Please enter a job description")])
    submit = SubmitField('Add')
           

class BiogForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="Please enter your name"), Length(max= 64, message="Please enter a shorter name")])
    email = EmailField('Email:', validators=[Email(message='Please enter a valid email'), InputRequired(message="Please enter an email"), Length(max=64, message="Please use a shorter email address")])
    area = StringField('Where do you live?', validators=[InputRequired(message="Please enter your location"), Length(max=32, message="Please enter somewhere shorter")])
    blurb = TextAreaField('Write a bit about yourself', validators=[InputRequired(message="Please enter something about yourself")])
    github = StringField('What is your github username?', validators=[Optional(), Length(max=32, message="Please use a shorter username")]) 
    linkedin = StringField('What is your LinkedIn username?', validators=[Optional(), Length(max=32, message="Please use a shorter username")]) 
    twitter = StringField('What is your twitter handle?', validators=[Optional(), Length(max=32, message="Please use a shorter username")])
    image_file = FileField('Please upload a picture of yourself', validators=[Optional()])
    cv_file = FileField('Please upload a PDF of your CV', validators=[Optional()])
    active = BooleanField(default=None)
    submit = SubmitField('Add')

    def validate_email(self, email):
        user = Biog.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address is already registered. Please try again.')

class SkillsForm(FlaskForm):
    biog_id = SelectField('Which user is this for?', validators=[InputRequired(message="Please select a user")])
    skill = StringField('Skill', validators=[InputRequired(message='Please enter a skill'), Length(max=64, message="The skill must be shorter than 64 characters. Please put more information in the description field below if required")])
    skill_description = TextAreaField('Describe a bit about that skill or qualification', validators=[InputRequired(message="Please provide some information or context about the skill")])
    submit = SubmitField('Add')

class ContactForm(FlaskForm):
    name = StringField('Name:', validators=[InputRequired(message="Please enter your name"), Length(max=64, message="Please enter a shorter name")])
    email = EmailField('Email:', validators=[Email(message='Please enter a valid email'), InputRequired(message="You must leave your email address"), Length(max=64, message="Please use a shorter email address")])
    organisation = StringField('Organisation:', validators=[Optional(), Length(max=64, message="Please use a shorter name for your organisation")])
    comment = TextAreaField('Please Write your Message:', validators=[InputRequired(message="Please enter a message")])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

class ChangeActiveUser(FlaskForm):
    biog_id = SelectField('Which user\'s biography should the website show?', validators=[InputRequired(message="Please select a user")])
    confirmation = BooleanField('I understand this will change the information displayed on the home screen', default=False, validators=[InputRequired(message="You must agree to this confirmation to proceed")])
    submit = SubmitField('Submit')

