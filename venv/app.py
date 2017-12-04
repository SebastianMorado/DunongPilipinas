from flask import Flask, render_template, flash, redirect, url_for, request, session, logging, get_flashed_messages
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from wtforms import Form, SubmitField, StringField, DecimalField, FloatField, DateTimeField, SelectField, BooleanField, IntegerField, PasswordField, validators
import time
from datetime import datetime
import operator
import simplejson as json
from passlib.hash import sha256_crypt
ops = {"<": operator.lt,
       ">": operator.gt,
       "=": operator.eq,
       "<=": operator.le,
       ">=": operator.ge}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DunongPilipinas.db'
db = SQLAlchemy(app)


class Region(db.Model):
    __tablename__ = 'region'
    province = db.Column('province', db.String(32), primary_key=True)
    region_name = db.Column('region_name', db.String(32))

    institutions = db.relationship('Institution', backref='region', lazy=True)

class Institution(db.Model):
    __tablename__ = 'institution'
    institution_id = db.Column('institution_id', db.Integer, primary_key=True)
    institution_name = db.Column('institution_name', db.String(128))
    street_address = db.Column('street_address', db.String(128))
    province = db.Column('province', db.String(32), db.ForeignKey('region.province'))
    district = db.Column('district', db.String(32))
    hei_type_name = db.Column('hei_type_name', db.String(32))

    offers = db.relationship('Offers', backref='institution', lazy=True)
    statistics = db.relationship('Statistics', backref='institution', lazy=True)
    contacts = db.relationship('Contact', backref='institution', lazy=True)
    users = db.relationship('User', backref='institution', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column('username', db.String(25), primary_key=True)
    password = db.Column('password', db.String(80))
    user_type = db.Column('user_type', db.String(12))
    institution_id = db.Column ('institution_id', db.Integer, db.ForeignKey('institution.institution_id'))

class Program(db.Model):
    __tablename__ = 'program'
    program_name = db.Column('program_name', db.String(128), primary_key=True)
    description = db.Column('description', db.String(128))
    duration = db.Column('duration', db.String(16))

    offers = db.relationship('Offers', backref='program', lazy=True)
    program_classifications = db.relationship('Program_Classification', backref='program', lazy=True)

class Sector(db.Model):
    __tablename__ = 'sector'
    sector_name = db.Column('sector_name', db.String(128), primary_key=True)
    sector_description = db.Column('sector_description', db.String(128))

    program_classifications = db.relationship('Program_Classification', backref='sector', lazy=True)

class Offers(db.Model):
    __tablename__ = 'offers'
    institution_id = db.Column('institution_id', db.Integer, db.ForeignKey('institution.institution_id'), primary_key=True)
    program_name = db.Column('program_name', db.String(128), db.ForeignKey('program.program_name'), primary_key=True)

class Statistics(db.Model):
    __tablename__ = 'statistics'
    institution_id = db.Column('institution_id', db.Integer, db.ForeignKey('institution.institution_id'), primary_key=True)
    year = db.Column('year', db.Integer, primary_key=True)
    tuition_per_unit = db.Column('tuition_per_unit', db.Float)
    num_of_enrollment = db.Column('num_of_enrollment', db.Integer)
    num_of_graduates = db.Column('num_of_graduates', db.Integer)
    num_of_faculty = db.Column('num_of_faculty', db.Integer)

class Program_Classification(db.Model):
    __tablename__ = "program_classification"
    program_name = db.Column('program_name', db.String(128), db.ForeignKey('program.program_name'), primary_key=True)
    sector_name = db.Column('sector_name', db.String(128), db.ForeignKey('sector.sector_name'), primary_key=True)

class Contact(db.Model):
    __tablename__ = 'contact'
    institution_id = db.Column('institution_id', db.Integer, db.ForeignKey('institution.institution_id'), primary_key=True)
    contact_person = db.Column('contact_person', db.String(64), primary_key=True)
    contact_num = db.Column('contact_num', db.String(64))



@app.route('/')
def index():
	list_insti = Institution.query.all()
	list_province = Region.query.all()
	return render_template('index.html', insti=list_insti, province=list_province)

@app.route('/search/', methods=['GET','POST'])
# @app.route('/search/q=<search_str>&page=<int:page>', methods=['GET','POST'])
@app.route('/search/q=<search_str>', methods=['GET','POST'])
def search(search_str="", page=1):
	limit = 200
	search_str_raw=[]
	search_prov =""
	search_region =""
	search_program=""

	if request.method == 'POST':
		search_str_raw = request.form.get('q').split(', Region')
		search_str = search_str_raw[0]
		page = int(request.form.get('page'))
		search_prov = request.form.get('province')
		search_region = request.form.get('region')
		search_program = request.form.get('offers')


	if(len(search_str_raw) > 1):
		raw_query = db.session.query(Institution,Region).filter(Institution.province == search_str).distinct().join(Region).filter(Institution.province == Region.province)
	else:
		raw_query = db.session.query(Institution,Region).filter(db.or_(Institution.institution_name.contains(search_str),Institution.province.contains(search_str))).distinct().join(Region).filter(Institution.province == Region.province)

	from_insti = raw_query.all()

	# If search matched a specific school, redirect
	if len(from_insti) == 1 and from_insti[0].Institution.institution_name == search_str:
		return redirect("/school/"+str(from_insti[0].Institution.institution_id))


	if(len(search_prov) > 0):
		raw_query = raw_query.filter(Institution.province == search_prov)

	if(len(search_region) > 0):
		raw_query = raw_query.filter(Region.region_name == search_region)

	from_insti = raw_query.all()
	from_insti_id = []
	for insti in from_insti:
		from_insti_id.append(insti.Institution.institution_id)

	if(len(search_program) > 0):
		raw_programs = db.session.query(Institution,Region,Offers).join(Region).join(Offers).filter(db.and_(Offers.program_name == search_program, Institution.institution_id.in_(from_insti_id)))
		from_insti = raw_programs.all()


	# Querying programs
	list_programs = db.session.query(Institution,Offers).join(Offers).distinct().all()

	## For pagination
	start = limit*(page-1)
	end = limit*(page-1)+limit

	paging={}
	paging['num_rows'] = len(from_insti)
	if len(from_insti) > end:
		from_insti=from_insti[start:end]
	else:
		end = len(from_insti)
		from_insti=from_insti[start:]
	paging['end'] = end
	if (len(from_insti) > 0):
		paging['start'] = start+1
	else:
		paging['start'] = start

	# For filter dropdown values
	list_region = db.session.query(Region.region_name).distinct().order_by(Region.region_name).all()
	list_province = Region.query.order_by(Region.province).all()
	list_offers = db.session.query(Program.program_name).distinct().order_by(Program.program_name).all()

	return render_template('results.html', results=from_insti, programs=list_programs, paging=paging, provinces=list_province, regions=list_region, courses=list_offers)

@app.route('/school/<int:school_id>')
def school(school_id):
	info = db.session.query(Institution,Region).filter(Institution.institution_id==school_id).join(Region).filter(Institution.province == Region.province).one()
	info_contact = db.session.query(Contact).filter(Contact.institution_id == school_id).all()

	info_programs = db.session.query(Offers,Program,Program_Classification).filter(Offers.institution_id == school_id).join(Program).join(Program_Classification).all()
	info_stats = db.session.query(Statistics).filter(Statistics.institution_id == school_id).order_by(Statistics.year).all()

	return render_template('school.html', info=info, contacts = info_contact, stats=info_stats, programs=info_programs)



class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    user_type = SelectField(
        'User Type',
        choices=[('admin', 'admin'), ('contributor', 'contributor')]
    )
    institution_id = IntegerField('Institution ID', [validators.DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        user_type = form.user_type.data
        institution_id = form.institution_id.data
        current_user = User.query.filter_by(username=username).first()
        if current_user:
            error = 'Username already taken'
            return render_template('register.html', form=form, error=error)
        else:
            new_user = User(username=username, password=password, user_type=user_type, institution_id=institution_id)
            db.session.add(new_user)
            db.session.commit()
            msg = "You are now registered and can log-in"
            return render_template('login.html', msg=msg)
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        current_user = User.query.filter_by(username=username).first()

        if current_user:
            # GET stored hash
            password = current_user.password
            #compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash("You are now registered and can log-in", 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Log-in', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

class MasterForm(Form):
    #Add Stat
    year = IntegerField('Year')
    tpu = FloatField('Tuition per Unit')
    noe = IntegerField('Number of Enrollment')
    nog = IntegerField('Number of Graduates')
    nof = IntegerField('Number of Faculty')
    submit1 = SubmitField('Submit')
    #Add Program
    program_name = StringField('Program Name')
    description = StringField('Description')
    duration = StringField('Duration')
    submit2 = SubmitField('Submit')
    #Add Contact
    contact_person = StringField('Contact Name')
    contact_num = StringField('Contact Number')
    submit3 = SubmitField('Submit')
    #Update Program
    update_program_name = StringField('Program Name')
    update_description = StringField('New Description')
    update_duration = StringField('New Duration')
    submit4 = SubmitField('Submit')
    #Update Statistic
    update_year = IntegerField('Year')
    update_tpu = FloatField('Tuition per Unit')
    update_noe = IntegerField('New Number of Enrollment')
    update_nog = IntegerField('New Number of Graduates')
    update_nof = IntegerField('New Number of Faculty')
    submit5 = SubmitField('Submit')



@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    form = MasterForm(request.form)
    username = session['username']
    user = db.session.query(User).filter(User.username==username).first()
    institution_id = user.institution_id
    insti_name = Institution.query.filter_by(institution_id=institution_id).first().institution_name
    contact_rows = db.session.query(User, Institution, Contact).filter(User.username==username).join(Institution).filter(User.institution_id == Institution.institution_id).join(Contact).filter(Institution.institution_id == Contact.institution_id).all()
    program_rows = db.session.query(User, Institution, Offers, Program).filter(User.username==username).join(Institution).filter(User.institution_id == Institution.institution_id).join(Offers).filter(Institution.institution_id == Offers.institution_id).join(Program).filter(Offers.program_name == Program.program_name).all()
    stat_rows = Statistics.query.filter_by(institution_id=institution_id).all()

    if request.method == 'POST':

        if form.submit1.data:
            year = form.year.data
            tpu = form.tpu.data
            noe = form.noe.data
            nog = form.nog.data
            nof = form.nof.data
            if Statistics.query.filter_by(year=year).filter_by(institution_id=institution_id).first():
                flash("ERROR: Statistics for this year already exist", 'error')
                return redirect(url_for('dashboard'))

            new_Stat = Statistics(institution_id=institution_id, year=year, tuition_per_unit=tpu, num_of_enrollment=noe, num_of_graduates=noe, num_of_faculty=nof)
            db.session.add(new_Stat)
            flash("Successfully added statistic!", 'success')

        elif form.submit2.data:
            program_name = form.program_name.data
            description = form.description.data
            duration = form.duration.data
            if Program.query.filter_by(program_name=program_name).first():
                if Offers.query.filter_by(program_name=program_name).filter_by(institution_id=institution_id).first():
                    flash("ERROR: Program is already offered", 'error')
                    return redirect(url_for('dashboard'))
                new_offer = Offers(institution_id=institution_id, program_name=program_name)
                db.session.add(new_offer)
            else:
                new_program = Program(program_name=program_name, description=description, duration=duration)
                db.session.add(new_program)
                new_offer = Offers(institution_id=institution_id, program_name=program_name)
                db.session.add(new_offer)
            flash("Successfully added program!", 'success')

        elif form.submit3.data:
            contact_person = form.contact_person.data
            contact_num = form.contact_num.data
            if Contact.query.filter_by(contact_person=contact_person).filter_by(institution_id=institution_id).first():
                flash("ERROR: Contact already exists", 'error')
                return redirect(url_for('dashboard'))
            new_contact = Contact(institution_id=institution_id, contact_person=contact_person, contact_num=contact_num)
            db.session.add(new_contact)
            flash("Successfully added contact!", 'success')

        elif form.submit4.data:
            program_name = form.update_program_name.data
            description = form.update_description.data
            duration = form.update_duration.data
            current_program = Program.query.filter_by(program_name=program_name).first()
            if current_program:
                if Offers.query.filter_by(program_name=program_name).filter_by(institution_id=institution_id).first():
                    if description:
                        current_program.description = description
                    if duration:
                        current_program.duration = duration
                else:
                    flash("ERROR: Not allowed to update program not offered by institution", 'error')
                    return redirect(url_for('dashboard'))
            else:
                flash("ERROR: Program does not exist", 'error')
                return redirect(url_for('dashboard'))
            flash("Successfully updated program!", 'success')

        elif form.submit5.data:
            year = form.update_year.data
            tpu = form.update_tpu.data
            noe = form.update_noe.data
            nog = form.update_nog.data
            nof = form.update_nof.data
            current_statistic = Statistics.query.filter_by(year=year).filter_by(institution_id=institution_id).first()
            if current_statistic:
                if tpu:
                    current_statistic.tuition_per_unit = tpu
                if noe:
                    current_statistic.num_of_enrollment = noe
                if nog:
                    current_statistic.num_of_graduates = nog
                if nof:
                    current_statistic.num_of_faculty = nof
            else:
                flash("ERROR: No data for this year exists yet", 'error')
                return redirect(url_for('dashboard'))
            flash("Successfully updated statistic!", 'success')

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', form=form, contact_rows=contact_rows, program_rows=program_rows, stat_rows=stat_rows, insti_id=institution_id, insti_name=insti_name)

@app.route('/dashboard/delete_contact/<row_id>', methods=['GET', 'POST'])
@is_logged_in
def delete_contact(row_id):
    username = session['username']
    user = db.session.query(User).filter(User.username==username).first()
    institution_id = user.institution_id
    new_row_id = row_id.replace('%20',' ')
    contact = db.session.query(Contact).filter(Contact.institution_id==institution_id).filter(Contact.contact_num==new_row_id).first()
    db.session.delete(contact)
    db.session.commit()
    print('Contact successfully deleted')
    return redirect(url_for('dashboard'))

@app.route('/dashboard/delete_program/<row_id>', methods=['GET', 'POST'])
@is_logged_in
def delete_program(row_id):
    username = session['username']
    user = db.session.query(User).filter(User.username==username).first()
    institution_id = user.institution_id
    new_row_id = row_id.replace('%20',' ')
    offered = db.session.query(Offers).filter(Offers.institution_id==institution_id).filter(Offers.program_name==new_row_id).first()
    db.session.delete(offered)
    db.session.commit()
    print('Program offered successfully deleted')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
