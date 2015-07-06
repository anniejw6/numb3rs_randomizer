from flask import (render_template, Flask, request,
	flash, session, redirect, url_for, g)
from app import app, forms, models, db, lm, bcrypt
from random import randint
from sqlalchemy import func
import pandas as pd
from flask.ext.login import (LoginManager, login_required, login_user,
	logout_user, current_user)
import json
from flask.ext.bcrypt import Bcrypt
import logging
import uuid
import sys
from numpy.random import RandomState
from datetime import datetime

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
lm.login_view = 'login'

@lm.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.
    :param unicode user_id: user_id (email) user to retrieve
    """
    #return models.User.query.filter_by(email = user_id).first()
    return models.User.query.get(user_id)

def randShots(seed):

	prng = RandomState(seed)
	treat = prng.randint(0, 2)
	if treat == 1:
		return('1 Shot')
	else:
		return(str(treat) + ' Shots')

# before request
@app.before_request
def before_request():

	if 'round' not in session:
		session['round'] = 0

	if 'session_idd' not in session:
		session['session_idd'] = uuid.uuid4().hex

	if current_user.is_authenticated():
		session['user_idd'] = session['user_id']
	else:
		session['user_idd'] = session['session_idd'] 

# Home Page
# Start New Round
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index/', methods = ['GET', 'POST'])
@login_required
def index():

	app.logger.info(session['round'])
	#app.logger.info(session['session_idd'])
	# seed = datetime.utcnow().microsecond
	# app.logger.info(randShots(seed))

	if request.method == 'GET':

		# Just the button
		return render_template('randomize_get.html')

	else:

		# Generate Treatment
		time = datetime.utcnow()
		seed = time.microsecond
		assignment = randShots(seed)

		# Add Round
		session['round'] = (session['round'] + 1)

		# Record Things
		assign = models.Assignment(
			session_id = session['session_idd'],
			user_id = session['user_idd'],
			time = str(time),
			seed = seed,
			outcome = assignment,
			round_num = session['round'])
		db.session.add(assign)
		db.session.commit()

		return render_template('randomize_post.html', treat = assignment)

# Record Errors
@app.route('/record/', methods = ['GET', 'POST'])
@login_required
def record():
	return render_template('record.html')

# Log-In & Register
@app.route("/login/", methods=["GET", "POST"])
def login():
	"""For GET requests, display the login form. 

	For POSTS, login the current user by processing the form."""

	form = forms.LoginForm()
	#app.logger.info(session['user_id'])

	if form.validate_on_submit():

		# Try to find user
		user = models.User.query.filter_by(name = form.name.data).first()
		app.logger.info(user)
		# If it exists, log in
		if user:

			user.authenticated = True
			app.logger.info('logged')
		# If it doesn't exist, register and log in
		else: 
			app.logger.info('registered')
			user = models.User(request.form['name'])
			db.session.add(user)
			db.session.commit()

		login_user(user, remember=True)
		session['user_idd'] = session['user_id']
		flash('User successfully registered')

		#app.logger.info(current_user)
		#app.logger.info(session['user_id'])

		return redirect(url_for("index"))

	return render_template("reg_login.html", form=form)

# Put responses in database
@app.route('/submission', methods=['POST'])
def submission():

	app.logger.info(request.form)

	time = str(datetime.utcnow())

	response = models.Response(
		session_id = session['session_idd'], 
		time = time,
		user_id = session['user_idd'], 
		num_err = int(request.form['num_err']),
		err_desc = request.form['err_descrip'],
		round_num = session['round'])

	db.session.add(response)
	db.session.commit()

	return str(len(models.Response.query.all()))

# Logout User
@app.route("/logout/", methods=["GET"])
@login_required
def logout():
	"""Logout the current user."""
	user = current_user
	user.authenticated = False
	db.session.add(user)
	db.session.commit()
	logout_user()
	session['user_idd'] = session['session_idd']
	session['round'] = 0
	return redirect(url_for("index"))