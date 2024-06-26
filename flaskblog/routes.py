from flask import render_template, flash, redirect, url_for, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateForm, PostForm
from flaskblog.models import User, Post
from flaskblog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os

@app.route("/")
@app.route("/home")
def home():
    # Paginate this query
    page = request.args.get('page', 1, type=int) # gets the page number from the URL
    #returns an object with posts ordered from most recent to old using order_by
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
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
            next_page = request.args.get('next') #gets the next key value from the url
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
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Uploaded', category='success')
        return redirect(url_for('home'))
    return render_template('post.html', form=form, title='Create post')

@app.route("/post/<int:post_id>/update>", methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)# return a value if exists else 404 page is showed up
    
    if post.author != current_user:
        abort(403) # Forbidden Route

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Updated Post Successfully', category='Success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        # autofill the fields with the values from the database
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post.html', form=form, title='update')

#route to access individual posts made by users
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('single.html', post=post)

# Route to delte a users post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # error page loads up regarding restricted permission to perform actions

    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', category='info')
    return redirect(url_for('home'))

# Route to display all posts from an user
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)