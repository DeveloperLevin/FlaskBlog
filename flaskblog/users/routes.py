from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request, abort
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateForm
from flaskblog.models import User, Post
from flaskblog import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.utils import save_picture

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # once the user is logged in, the register button will redirect to home page
    form = RegistrationForm()
    if form.validate_on_submit():
        #generates hashed password with bcrypt and creates a new instance in user column and commits the transaction to the database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Account created for {form.username.data}", category="success")
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home')) # once the user is logged in, the login button will redirect to home page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #gets the next key value from the url
            flash("You've logged in", category='success')
            return redirect(next_page) if next_page else redirect(url_for('main.home')) #after loggin in the user, it redirects to the page the user was viewing before loggin in
        else:
            flash('Unsuccessful Login', category='danger')
    return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required #decorator from flask-login, that requires you to login to access this route
def account():
    image_file = url_for('static', filename='images/'+ current_user.image_file) # gets us the address of the image from static based on what was stored in the database, else produces a default pic
    form = UpdateForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Updated', category='success')
        return redirect(url_for('users.account')) # this makes the browser send a get request instead of the default post request when submitting a form
    
    elif request.method == 'GET':
        # when a get request is sent, it populates the form fields with current user's credentials
        form.username.data = current_user.username
        form.email.data = current_user.email    
    return render_template('account.html', image_file=image_file, form=form)


# Route to display all posts from an user
@users.route("/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)