from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request, abort
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post
from flaskblog import db
from flask_login import current_user, login_required


posts = Blueprint('posts', __name__)


@posts.route("/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Uploaded', category='success')
        return redirect(url_for('main.home'))
    return render_template('post.html', form=form, title='Create post')

@posts.route("/<int:post_id>/update", methods=['GET', 'POST'])
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
        flash('Updated Post Successfully', category='success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        # autofill the fields with the values from the database
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post.html', form=form, title='update', post=post)

#route to access individual posts made by users
@posts.route("/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('single.html', post=post)

# Route to delte a users post
@posts.route("/<int:post_id>/delete", methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # error page loads up regarding restricted permission to perform actions

    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', category='info')
    return redirect(url_for('main.home'))