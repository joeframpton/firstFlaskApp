from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask_login import logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc
from sqlalchemy.sql.functions import coalesce
import datetime
from ..models import Admin, Biog, Work, Skills, Contact
from ..forms import AdminRegistrationForm, WorkForm, BiogForm, SkillsForm, ChangeActiveUser
from ..extensions import db


def choices_list_orderer(id):
    """In SelectField, the preloading of data is overruled by the list of choices. This queries the database to produce a list of tuples where the inputted id will be at the top of the list, and therefore the default. 

    Args:
        id (int): The biog id of name that should at the 0th index of the list

    Returns:
        List of tuples: Where tuples are (id, name) where the desired pre-loaded biog_id is the de-facto default.
    """
    raw_choices =  [(biog.id, biog.name) for biog in Biog.query.all()]
    list_of_choices = [raw_choices.pop(index) for index, tup in enumerate(raw_choices) if tup[0] == id]
    list_of_choices.extend(raw_choices)
    return list_of_choices

def active_user_generator():
    """Generates the active user as defined on the dashboard

    Returns:
        Object: Object of the model Biog
    """
    active_user = Biog.query.filter_by(active=1).first()
    return active_user

#Implementation of sqlalchemy's coalesce was from: http://progblog10.blogspot.com/2014/06/handling-null-values-in-sqlalchemy.html
def active_user_orderer():
    """Queries the database to produce a list of tuples where the current active user is at the top of the list, and therefore the default. 

    Returns:
        List of Tuples: Where tuples are (id, name)
    """
    return [(x.id, x.name) for x in Biog.query.order_by(asc(coalesce(Biog.active, 2)))]

admin = Blueprint('admin', __name__, url_prefix='/admin')

#The blueprint login restriction idea is from: https://michaelabrahamsen.com/posts/enforcing-login-on-all-flask-blueprint-routes/
@admin.before_request
@login_required
def restricted_view(): 
    pass

@admin.errorhandler(401)
def unauthorised(e):
    flash('You must be logged in to access the admin area')
    return redirect(url_for('public.login')), 401

@admin.errorhandler(500)
def servererror(e):
    flash('There has been an error. Please try again')
    return(redirect(url_for('admin.biog')))

@admin.route('/', methods=['GET', 'POST'])
def dashboard():
    active_user = active_user_generator()
    form = ChangeActiveUser()
    form.biog_id.choices = active_user_orderer()
    contacts = Contact.query.filter_by(biog_id=active_user.id).order_by(desc(Contact.id)).all()

    if form.validate_on_submit():
        #Check if there's an active user currently then to remove them as active:
        if Biog.query.filter_by(active=1).first():
            active_user_generator()
            active_user.active = None
            flash(f'{active_user.name}\'s portfolio is no longer being displayed')
            db.session.commit()
        new_active = Biog.query.get_or_404(form.biog_id.data)
        new_active.active = True
        db.session.commit()
        flash(f'Webpage now showing {new_active.name}\'s portfolio!')
        return redirect(url_for('admin.dashboard'))
    return render_template('dash.html', contacts=contacts, form=form, active_user=active_user)

@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('public.login'))

@admin.route('/admins', methods=['GET','POST'])
def admins():
    active_user = active_user_generator()
    admins = Admin.query.all()
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        admin = Admin(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('admin.admins'))
    return render_template('admins.html', form=form, admins=admins, active_user=active_user)

#deleting forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('/admins/delete/<int:id>')
def delete_admin(id):
    current_id = current_user.id
    #The site can't be without an admin
    if  id > 1:
        admin = Admin.query.get_or_404(id)
        db.session.delete(admin)
        db.session.commit()
        if id == current_id:
            flash('You have deleted your own account')
            return redirect(url_for('public.home'))
        flash('Admin deleted')    
        return redirect(url_for('admin.admins'))
    else:
        flash('You can\'t delete the primary admin')
        return redirect(url_for('admin.admins'))

@admin.route('/biog', methods=['GET','POST'])
def biog():
    active_user = active_user_generator()
    biogs = Biog.query.all()
    form = BiogForm()
    if form.validate_on_submit():
        image_filename = image_data = cv_filename = cv_data = None
        image_file = request.files['image_file']
        if image_file and not Biog.allowed_file_img(image_file.filename):
            flash('Incorrect file type attached. Please only upload images that are .JPG, .JPEG or .PNG')
            return redirect(url_for('admin.biog'))

        image_filename = secure_filename(image_file.filename)
        image_data = image_file.read()
        image_mimetype = image_file.mimetype

        cv_file = request.files['cv_file']
        if cv_file and not Biog.allowed_file_cv(cv_file.filename):
            flash('Incorrect file type attached. Please only upload CVs in a PDF format')
            return redirect(url_for('admin.biog'))

        cv_filename = secure_filename(cv_file.filename)
        cv_data = cv_file.read()
      
        biog = Biog(name=form.name.data, email=form.email.data, area=form.area.data, blurb=form.blurb.data, github=form.github.data, linkedin=form.linkedin.data, twitter=form.twitter.data, image_filename=image_filename, image_data=image_data, image_mimetype = image_mimetype, cv_filename=cv_filename, cv_data=cv_data)
        db.session.add(biog)
        db.session.commit()
        flash(f'{biog.name} added!')
        return redirect(url_for('admin.biog'))
    return render_template('biog.html', form=form, biogs=biogs, active_user=active_user)

#Updating forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('biog/<int:id>', methods=['GET', 'POST'])
def biog_update(id):
    active_user = active_user_generator()
    form = BiogForm()
    biog_to_update = Biog.query.get_or_404(id)
    #preloading the form with the existing data that is to be edited
    form.name.data = biog_to_update.name
    form.email.data = biog_to_update.email
    form.area.data = biog_to_update.area
    form.blurb.data = biog_to_update.blurb
    form.github.data = biog_to_update.github
    form.linkedin.data = biog_to_update.linkedin
    form.twitter.data = biog_to_update.twitter
    
    #update labels
    form.submit.label.text = 'Update'
    if not biog_to_update.image_filename == '':
        form.image_file.label.text = 'You have already uploaded a picture. If you would like to update it, please upload a new picture of yourself.'
    if not biog_to_update.cv_filename == '':
        form.cv_file.label.text = 'You have already uploaded a CV. If you would like to update it, please upload a new CV.'    

    if request.method == 'POST':
        biog_to_update.name = request.form['name']
        biog_to_update.email = request.form['email']
        biog_to_update.area = request.form['area']
        biog_to_update.blurb = request.form['blurb']
        biog_to_update.github = request.form['github']
        biog_to_update.linkedin = request.form['linkedin']
        biog_to_update.twitter = request.form['twitter']
        
        if request.files['image_file']:
            image_file = request.files['image_file']
            if image_file and not Biog.allowed_file_img(image_file.filename):
                flash('Incorrect file type attached. Please only upload images that are .JPG, .JPEG or .PNG')
                return redirect(url_for('admin.biog_update', id=biog_to_update.id))
            biog_to_update.image_filename = secure_filename(image_file.filename)
            biog_to_update.image_data = image_file.read()
            biog_to_update.image_mimetype = image_file.mimetype
            
        if request.files['cv_file']:
            cv_file = request.files['cv_file']
            if cv_file and not Biog.allowed_file_cv(cv_file.filename):
                flash('Incorrect file type attached. Please only upload CVs in a PDF format')
                return redirect(url_for('admin.biog_update', id=biog_to_update.id))
            biog_to_update.cv_filename = secure_filename(cv_file.filename)
            biog_to_update.cv_data = cv_file.read()

        try: 
            db.session.commit()
            flash(f'Updated {biog_to_update.name}\'s profile')
            return redirect(url_for('admin.biog_update', id=biog_to_update.id))
        except:
            flash('Unable to update profile')
            return redirect(url_for('admin.biog_update', id=biog_to_update.id))
    return render_template('biog_update.html', form=form, biog_to_update=biog_to_update, active_user=active_user)

#deleting forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('/biog/delete/<int:id>')
def biog_delete(id):
    biog_to_delete = Biog.query.get_or_404(id)
    name = biog_to_delete.name
    Skills.query.filter_by(biog_id=id).delete()
    Work.query.filter_by(biog_id=id).delete()
    db.session.delete(biog_to_delete)
    db.session.commit()
    flash(f'{name} has been deleted')
    return redirect(url_for('admin.biog'))


@admin.route('/work', methods=['GET','POST'])
def work():
    active_user = active_user_generator()
    try:
        works = Work.query.all()
        form = WorkForm()
        #To ensure the default person to show is the current 'active' biog 
        form.biog_id.choices = active_user_orderer()
        if form.validate_on_submit():
            work = Work(title=form.title.data, company=form.company.data, start=form.start.data, end=form.end.data, job_description=form.job_description.data, biog_id=form.biog_id.data)
            db.session.add(work)
            db.session.commit()
            flash('Work Experience added')
            return redirect(url_for('admin.work'))  
        return render_template('work.html', form=form, works=works, active_user=active_user)
    except:
        flash('There has been an error. Make sure you\'ve added a person first')
        return(redirect(url_for('admin.biog')))

#Updating forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('work/<int:id>', methods=['GET','POST'])
def work_update(id):
    active_user = active_user_generator()
    form = WorkForm()
    work_to_update = Work.query.get_or_404(id)
    #reorder the choices list so that the current work owner is preloaded
    form.biog_id.choices = choices_list_orderer(work_to_update.biog_id)
    #preloading the rest of the form with the existing data that is to be edited
    form.title.data = work_to_update.title
    form.company.data = work_to_update.company
    form.start.data = work_to_update.start
    form.end.data = work_to_update.end
    form.job_description.data = work_to_update.job_description
    #Amending the labels
    form.submit.label.text = 'Update'

    if form.validate_on_submit():
        work_to_update.biog_id = request.form['biog_id']
        work_to_update.title = request.form['title']
        work_to_update.company = request.form['company']
        #need to convert dates from Werkzeug Data type to datetime
        work_to_update.start= datetime.date.fromisoformat(request.form['start'])
        if request.form['end']:
            work_to_update.end = datetime.date.fromisoformat(request.form['end'])
        work_to_update.job_description = request.form['job_description']
        try: 
            db.session.commit()
            flash('Updated employment')
            return redirect(url_for('admin.work_update', id=work_to_update.id, active_user=active_user))
        except:
            flash('Unable to update employment')
            return redirect(url_for('admin.work_update', id=work_to_update.id))
    else:
        print(form.errors)
    return render_template('work_update.html', form=form, work_to_update=work_to_update, active_user=active_user)


#deleting forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('/work/delete/<int:id>')
def work_delete(id):
    work_to_delete = Work.query.get_or_404(id)
    db.session.delete(work_to_delete)
    db.session.commit()
    flash('Work history entry deleted')
    return redirect(url_for('admin.work'))


@admin.route('/skills', methods=['GET','POST'])
def skills():
    active_user = active_user_generator()
    skills = Skills.query.all()
    form = SkillsForm()
    form.biog_id.choices = active_user_orderer()
    if form.validate_on_submit():
        skill = Skills(skill=form.skill.data, skill_description=form.skill_description.data, biog_id=form.biog_id.data)
        db.session.add(skill)
        db.session.commit()
        flash('Skill added')
        return redirect(url_for('admin.skills'))  
    return render_template('skills.html', form=form, skills=skills, active_user=active_user)

#Updating forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('/skills/<int:id>', methods=['GET', 'POST'])
def skills_update(id):
    active_user = active_user_generator()
    form = SkillsForm()
    skill_to_update = Skills.query.get_or_404(id)
    #reorder the choices list so that the current skill owner is preloaded
    form.biog_id.choices = choices_list_orderer(skill_to_update.biog_id)
    #preloading the rest of the form with the existing data that is to be edited
    form.skill.data = skill_to_update.skill
    form.skill_description.data = skill_to_update.skill_description 
    #update label
    form.submit.label.text = 'Update'

    if form.validate_on_submit():
        skill_to_update.biog_id = request.form['biog_id']
        skill_to_update.skill = request.form['skill']
        skill_to_update.skill_description = request.form['skill_description']
        try: 
            db.session.commit()
            flash('Updated skill')
            return redirect(url_for('admin.skills_update', id=skill_to_update.id))
        except:
            flash('Unable to update skill')
            return redirect(url_for('admin.skills_update'))

    return render_template('skills_update.html', form=form, skill_to_update=skill_to_update, active_user=active_user)


#deleting forms adapted from flatplanet's code: https://github.com/flatplanet/flasker/blob/main/app.py
@admin.route('/skills/delete/<int:id>')
def skills_delete(id):
    skill_to_delete = Skills.query.get_or_404(id)
    db.session.delete(skill_to_delete)
    db.session.commit()
    flash('Skill deleted')
    return redirect(url_for('admin.skills'))