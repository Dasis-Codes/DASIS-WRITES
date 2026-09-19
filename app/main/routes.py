import os
from flask import render_template, request, Blueprint, current_app, send_from_directory
from app.models import Post

from flask import Blueprint

main= Blueprint('main',__name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@main.route("/about")
def about():
    return render_template("about.html", title="About")


@main.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "pics"),
        "favicon.png",
        mimetype="image/png",
    )
