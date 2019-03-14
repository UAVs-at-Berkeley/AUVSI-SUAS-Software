from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db
from app import app
from app.forms import DataForm
from app.models import User
from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)


@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    form = DataForm()
    if request.method == 'POST':
        user = User(username=form.username.data, email=form.email.data, time=datetime.now())
        db.session.add(user)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('login.html', title='Sign In', form=form)

@app.route('/recent')
def recent():
    user = User.query.order_by(User.time.desc()).first()
    return jsonify(username = user.username, email = user.email, time=user.time)
