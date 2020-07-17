from app import app

from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask import request
from flask import send_from_directory

from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required

from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import FileForm

from app.models import User
from app.models import File
from app import db

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from uuid import uuid4

from datetime import datetime
from datetime import timedelta

import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = FileForm()
    if form.validate_on_submit():
        print('Form successfully validated.')
        f = form.file.data
        filename = secure_filename(f.filename)
        id = str(uuid4())
        path = os.path.join(app.instance_path, 'files', id)
        file = File(
            id = id,
            user_id = current_user.id,
            path = path,
            expire_time = datetime.utcnow() + timedelta(minutes = int(form.expiration.data)),
            name = filename
        )
        db.session.add(file)
        db.session.commit()
        print('File added to db.')
        f.save(path)
        print('FIle saved.')
        flash('Successfully uploaded your file!')
        return redirect(url_for('index'))
    return render_template('index.html', title = 'Welcome', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username = form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulation, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    files = current_user.uploaded_files().all()
    for file in files:
        file.is_expired()
    sizes = {}
    files = current_user.uploaded_files().all()
    for file in files:
        sizes[file.id] = file.size()
        
    return render_template('user.html', user=user, files=files, sizes=sizes)


@app.route('/file/<fileid>', methods=['GET', 'POST'])
def filepage(fileid):
    file = File.query.filter_by(id=fileid).first_or_404()
    size = file.size()
    return render_template('file.html', file=file, size=size)


@app.route('/download/<fileid>', methods=['GET', 'POST'])
def download(fileid):
    uploads = os.path.join(app.instance_path, 'files')
    file = File.query.filter_by(id=fileid).first_or_404()
    return send_from_directory(
        directory=uploads, 
        filename=file.id,
        as_attachment = True,
        attachment_filename = file.name
        )
