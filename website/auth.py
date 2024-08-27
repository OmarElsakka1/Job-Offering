from flask import send_file
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db  # means from __init__.py import db
from .helpers import CheckTypicality, CheckLength, Passwords, CheckEmail
from .user_system import userSystem


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if Passwords(
                    user.password,
                    password).is_same(
                    'Logged in successfully!',
                    'Incorrect password, try again.'):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    dropdown_options = ['Freelancer', 'Business Owner', 'Both']
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        gender = request.form['gender']
        usertype = request.form['usertype']
        about = request.form.get('job_description')

        user = User.query.filter_by(email=email).first()
        is_good_pass = Passwords(password1, password2).is_good()
        is_good_email = CheckEmail().is_in_form(email, True)

        firstcheck = CheckLength(2, "First name").is_short(first_name)
        lastcheck = CheckLength(2, "Last name").is_short(last_name)
        jobcheck = CheckLength(4, "Job Description").is_short(about)
        if user:
            flash('Email already exists!', category='error')
        # Demorgan
        elif firstcheck or lastcheck or jobcheck or not(is_good_email and is_good_pass):
            pass
        elif CheckTypicality(gender, "").is_equal():
            flash('You have to choose a Gender!', category='error')
        elif CheckTypicality(usertype, "").is_equal():
            flash('You have to choose a User Type!', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                about=about,
                gender=gender,
                usertype=usertype,
                password=generate_password_hash(
                    password1,
                    method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created Successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template(
        "sign_up.html",
        user=current_user,
        dropdown_options=dropdown_options)


@auth.route('/changeprofile', methods=['GET', 'POST'])
@login_required
def change_profile():
    dropdown_options = ['Freelancer', 'Business Owner', 'Both']
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        gender = request.form['gender']
        usertype = request.form['usertype']
        about = request.form.get('job_description')
        file = request.files['file']

        user = User.query.filter_by(id=current_user.id).first()
        is_good_email = CheckEmail().is_in_form(email, not CheckTypicality(email, ""))

        if len(email) == 0 or not is_good_email:
            pass
        elif not (CheckTypicality(email, current_user.email).is_equal() or User.query.filter_by(email=email).first()):
            user.email = email
            db.session.commit()
            flash('Email changed Successfully!', category='success')

        if len(first_name) == 0:
            pass
        elif not (CheckLength(2, "First name").is_short(first_name, showmsg=not CheckTypicality(first_name, "").is_equal()) or CheckTypicality(first_name, current_user.first_name).is_equal()):
            user.first_name = first_name
            db.session.commit()
            flash('First name changed Successfully!', category='success')

        if len(last_name) == 0:
            pass
        elif not (CheckLength(2, "Last name").is_short(last_name, showmsg=not CheckTypicality(last_name, "").is_equal()) or CheckTypicality(last_name, current_user.last_name).is_equal()):
            user.last_name = last_name
            db.session.commit()
            flash('Last name changed Successfully!', category='success')

        if not (
            CheckLength(
                4,
                "Job Description").is_short(
                about,
                showmsg=not CheckTypicality(
                about,
                "").is_equal()) or CheckTypicality(
                    about,
                current_user.about).is_equal()):
            user.about = about
            db.session.commit()
            flash('Job Description updated Successfully!', category='success')

        if not (
            CheckTypicality(
                gender,
                current_user.gender).is_equal() or CheckTypicality(
                gender,
                "").is_equal()):
            user.gender = gender
            db.session.commit()
            flash('Gender updated Successfully!', category='success')
        if not (
            CheckTypicality(
                usertype,
                current_user.usertype).is_equal() or CheckTypicality(
                usertype,
                "").is_equal()):
            user.usertype = usertype
            db.session.commit()
            flash('User Type updated Successfully!', category='success')

        if (file.filename):
            filename = file.filename
            img_format = filename[-3:]
            if (filename and (
                    (filename[-3:] in ['png', 'jpg', 'gif']) or (filename[-4:] == 'jpeg'))):
                if userSystem.ChangePfp(current_user, file):
                    flash('Image uploaded successfully', category='success')
            else:
                flash(
                    'Invalid Image format (Should be .jpg).',
                    category='error')

        return redirect(url_for('auth.change_profile'))
    return render_template(
        "change_profile.html",
        user=current_user,
        dropdown_options=dropdown_options)


@auth.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        email = current_user.email
        password = request.form.get('password')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(id=current_user.id).first()

        is_good = Passwords(password1, password2).is_good()
        is_old_correct = Passwords(
            user.password, password).is_same(
            "", 'Old Password is wrong.')
        if (is_good and is_old_correct):
            new_password_hash = generate_password_hash(password1)
            user.password = new_password_hash
            db.session.commit()
            flash('Password Changed Successfully!', category='success')
            return redirect(url_for('job_views.browse_jobs'))

    return render_template("change_password.html", user=current_user)


@auth.route('/image/<int:user_id>')
@login_required
def get_image(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        try:
            # return send_file(BytesIO(user.image_data), mimetype='image/jpeg')
            return send_file(
                f'../instance/Images/{user_id}.jpg',
                mimetype='image/jpg')
        except BaseException:
            try:
                return send_file(
                    f'../instance/Images/{user_id}.png',
                    mimetype='image/jpg')
            except BaseException:
                try:
                    return send_file(
                        f'../instance/Images/{user_id}.gif',
                        mimetype='image/jpg')
                except BaseException:
                    try:
                        return send_file(
                            f'../instance/Images/{user_id}.jpeg',
                            mimetype='image/jpg')
                    except BaseException:
                        return send_file(
                            'static/Images/default_profile_image.png',
                            mimetype='image/jpg')