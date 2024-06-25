from flask import render_template, flash, redirect, url_for, request
from flaskblog.forms import RegistrationForm, LoginForm, UpdateForm, PostForm
from flaskblog.models import User, Post
from flaskblog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 21, 2018'
    },
    {
        'author': 'Levin Moras',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2024'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # once the user is logged in, the login button will redirect to home page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #gets the next key vaalue from the url
            flash("You've logged in", category='success')
            return redirect(next_page) if next_page else redirect(url_for('home')) #after loggin in the user, it redirects to the page the user was viewing before loggin in
        else:
            flash('Unsuccessful Login', category='danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

#adds the picture to the static directory
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    #Transforms the image to fit the tuple size 
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
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
        flash('Account Updated', category='Success')
    elif request.method == 'GET':
        # when a get request is sent, it populates the form fields with current user's credentials
        form.username.data = current_user.username
        form.email.data = current_user.email
        return redirect(url_for('account')) # this makes the browser send a get request instead of the default post request when submitting a form
    return render_template('account.html', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate__on_submit():
        post = Post(title=form.title.data, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        flash('Post Uploaded', category='Success')
        return redirect('home')
    return render_template('post.html', form=form)