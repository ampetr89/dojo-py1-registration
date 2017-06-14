from flask import Flask, redirect, render_template, request, session, flash
import re
from datetime import datetime as dt

secret_key = open('secret-key.txt', 'r').read().strip()
app = Flask(__name__)
app.secret_key = secret_key

@app.route('/')
def index():
	session['form'] = {}
	session['success'] = False
	return render_template('index.html')

def valid_password(pw):
	"""
	at least 1 uppercase letter and 1 numeric value.
	"""
	longEnough = len(pw) > 8
	hasUpper = pw.lower() != pw.upper()
	hasNumber = not pw.isalpha()
	# could add more checks..
	valid = [longEnough, hasUpper, hasNumber]

	return all(valid)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
BDAY_REGEX =re.compile('\d\d\d\d-\d\d-\d\d')

@app.route('/process', methods=['POST'])
def process():
	"""
	All fields are required and must not be blank
	First and Last Name cannot contain any numbers
	Password should be more than 8 characters
	Email should be a valid email
	Password and Password Confirmation should match
	"""
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	birthday = request.form['birthday']
	password1 = request.form['password1']
	password2 = request.form['password2']

	field_names = {
		'first_name': 'First name',
		'last_name': 'Last name',
		'email': 'Email address',
		'birthday': 'Birthday',
		'password1': 'Password',
		'password2': 'Password confirmation'
	}

	blank = []
	for field, name in field_names.items():
		if len(request.form[field]) == 0:
			flash(name+' field is required')
			blank.append(field)

	#if len(blank) > 0:
		# dont bother checking the rest
		#return redirect('/')

	errors = 0
	if 'first_name' not in blank and not first_name.isalpha():
		flash('First name cannot contain any numbers')
		errors += 1

	if 'last_name' not in blank and not last_name.isalpha():
		flash('Last name cannot contain any numbers')
		errors += 1

	if 'email' not in blank and not EMAIL_REGEX.match(email):
		flash('Email address is not valid')
		errors += 1

	if 'birthday' not in blank:
		if not BDAY_REGEX.match(birthday):
			errors += 1
			flash('Birthday should be formatted as YYYY-mm-dd')
		else:
			try:
				bday = dt.strptime(birthday, '%Y-%m-%d').date()
				if bday > dt.now().date():
					errors += 1
					flash('Birthday must be in the past')
			except Exception as err:
				errors += 1
				flash('Invalid date entered for birthday')



	if 'password1' not in blank and not valid_password(password1):
		flash('Password must be more than 8 characters, contain at least 1 number and at least 1 uppercase letter.')

	if 'password2' not in blank and password1 != password2:
		flash("Password and confirmation don't match")

	if errors == 0 and len(blank) == 0:
		session['success'] = True
		session['form'] = dict(list(request.form.items()))
		return redirect('/success')
	else:
		return redirect('/')


@app.route('/success')
def success():
	if session['success']:
		form = session['form']
		vals = {
			'first_name': form['first_name'],
			'last_name': form['last_name'],
			'email': form['email']
		}
		return render_template('success.html', **vals)
	else:
		return redirect('/')

app.run(debug=True)
