from flask import send_file
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
import pandas as pd
import matplotlib.pyplot as plt
from .models import User, Admin
from . import db
from .helpers import CheckLength, Passwords, CheckEmail
from .user_system import userSystem


admin = Blueprint('admin', __name__)


@admin.route('/admin')
def func():
    return redirect(url_for('admin.login'))


@admin.route('/adminlogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Admin.query.filter_by(email=email).first()
        if user:
            if Passwords(
                    user.password,
                    password).is_same(
                    'Logged in successfully!',
                    'Incorrect password, try again.'):
                login_user(user, remember=True)

                # return redirect(url_for('admin.add_acount'))
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Email does not exist.', category='error')

    return render_template("Admin_login.html", user=current_user)


@admin.route('/adminlogout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/admindashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    users = User.query.all()
    user_dicts = [user.__dict__ for user in users]
    df = pd.DataFrame(user_dicts)
    gender_counts = df['gender'].value_counts()
    gender_counts_df = gender_counts.to_frame().reset_index()

    usertype_counts = df['usertype'].value_counts()
    usertype_counts_df = usertype_counts.to_frame().reset_index()

    gender_counts = df['gender'].value_counts()
    print(gender_counts)
    try:
        # Plot the counts using matplotlib
        gender_counts.plot(kind='bar')
        plt.xlabel('Gender')
        plt.ylabel('Count')
        plt.title('Gender Counts')
        plt.savefig('instance/Statistics/GenderDistribution.png')

        usertype_counts.plot(kind='bar')
        plt.xlabel('User Types')
        plt.ylabel('Count')
        plt.title('User Types Counts')
        plt.savefig('instance/Statistics/UserDistribution.png')
    except BaseException:
        print("Error happened")
        pass

    return render_template(
        "Admin_dashboard.html",
        usertype_counts_df=usertype_counts_df,
        gender_counts_df=gender_counts_df,
        user=current_user)


@admin.route('/adminusers', methods=['GET', 'POST'])
@login_required
def admin_users():
    users = User.query.all()
    return render_template('Admin_users.html', users=users, user=current_user)


@admin.route('/adminadd_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Admin.query.filter_by(email=email).first()
        is_good_pass = Passwords(password1, password2).is_good()
        is_good_email = CheckEmail().is_in_form(email, showmsg=True)

        firstcheck = CheckLength(2, "First name").is_short(first_name)
        lastcheck = CheckLength(2, "Last name").is_short(last_name)

        if user:
            flash('Email already exists!', category='error')
        # Demorgan
        elif firstcheck or lastcheck or not(is_good_email and is_good_pass):
            pass
        else:
            new_user = Admin(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(
                    password1,
                    method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('admin.dashboard'))

    return render_template("Admin_add_admin.html", user=current_user)


@admin.route('/adminchangepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        email = current_user.email
        password = request.form.get('password')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Admin.query.filter_by(id=current_user.id).first()

        is_good = Passwords(password1, password2).is_good()
        is_old_correct = Passwords(
            user.password, password).is_same(
            "", 'Old Password is wrong.')
        if (is_good and is_old_correct):
            new_password_hash = generate_password_hash(password1)
            user.password = new_password_hash
            db.session.commit()
            flash('Password Changed Successfully!', category='success')
            return redirect(url_for('admin.change_password'))

    return render_template("Admin_change_password.html", user=current_user)


@admin.route('/adminremove_user', methods=['GET', 'POST'])
@login_required
def remove_user():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            print(user)
            print(user.email)
            if userSystem.DeleteUser(user.id):
                flash('Deleted Successfully.', category='success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash("Error", category='error')

    return render_template("Admin_delete_user.html", user=current_user)


@admin.route('/adminbrowseposts', methods=['GET', 'POST'])
@login_required
def browseposts():
    return render_template("Admin_browse_posts.html", user=current_user)


@admin.route('/image/<string:name>')
@login_required
def get_image(name):
    return send_file(
        f'../instance/Statistics/{name}.png',
        mimetype='image/jpg')