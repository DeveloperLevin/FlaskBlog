from flask import Blueprint
from flask import render_template, request
from flaskblog.models import Post

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    # Paginate this query
    page = request.args.get('page', 1, type=int) # gets the page number from the URL
    #returns an object with posts ordered from most recent to old using order_by
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', posts=posts)