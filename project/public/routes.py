from flask import Blueprint, render_template, redirect, url_for, flash, send_file, Response
from flask_login import login_user
from sqlalchemy import desc
from io import BytesIO
import smtplib
from ..models import Biog, Work, Skills, Contact, Admin
from ..forms import LoginForm, ContactForm
from ..extensions import db

public = Blueprint('public', __name__)

def active_user_generator():
    """Generates the active user as defined on the dashboard

    Returns:
        Object: Object of the model Biog
    """
    active_user = Biog.query.filter_by(active=1).first()
    return active_user

@public.route('/')
def home():
    active_user = active_user_generator()
    active_image = BytesIO(active_user.image_data)
    works = Work.query.filter_by(biog_id=active_user.id).order_by(desc(Work.start)).all()
    skills = Skills.query.filter_by(biog_id=active_user.id)
    return render_template('home.html', works=works, skills=skills, active_user=active_user, active_image=active_image)

#Image loading from https://www.youtube.com/watch?v=zMhmZ_ePGiM&t=506s
@public.route('/img/<int:id>')
def image(id):
    user = Biog.query.get_or_404(id)
    return Response(user.image_data, mimetype=user.image_mimetype)


@public.route('/login', methods = ['GET', 'POST'])
def login():
    active_user = active_user_generator()
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin:
            if Admin.verify_password(admin, form.password.data):
                login_user(admin, remember=form.remember_me.data) 
                flash('Logged in!')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Your password is incorrect')
        else:
            flash('That admin accout does not exist')
    return render_template('login.html', form=form, active_user=active_user)

#Code adapted from https://flask.palletsprojects.com/en/2.2.x/api/?highlight=send_file#flask.send_file
@public.route('/downloadCV')
def download():
    active_user = active_user_generator()
    if active_user.cv_filename == '':
       flash(f'{active_user.name} does not have a CV available to download at the moment')
       return redirect(url_for('public.home')) 
    return send_file(BytesIO(active_user.cv_data), as_attachment=True, download_name=active_user.cv_filename) 

@public.route('/contact_me', methods=['GET','POST'])
def contact_me():
    active_user = active_user_generator()
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(name=form.name.data, organisation=form.organisation.data, email=form.email.data, comment=form.comment.data, biog_id=active_user.id)
        db.session.add(contact)
        db.session.commit()    

        #SMTP code adapted from: https://stackoverflow.com/questions/1546367/python-how-to-send-mail-with-to-cc-and-bcc
        website_email = 'autoresponse.jf@outlook.com'
        bcc = [active_user.email]
        response = f'AUTO-RESPONSE\n___________\nHi {contact.name},\nThank you for getting in touch. I will reply as soon as I can.\n\nDiolch,\n{active_user.name}\n\nFor reference, your message to me was:\n'
        email_response = f'From: {website_email}\nTo:{contact.email} \nSubject: Autoresponse to your query\n\n'+ response + form.comment.data
        to_address = [contact.email] + bcc
        server=smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(website_email, 'JoeFramptonwebsite2023')
        server.sendmail(website_email, to_address, email_response)
        server.quit()

        flash('Thank you for contacting me.')
        return redirect(url_for('public.contact_me'))
    return render_template('contact_me.html', form=form, active_user=active_user)
