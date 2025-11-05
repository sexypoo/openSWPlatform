from flask import Blueprint, render_template

pages_bp = Blueprint("pages",__name__)

@pages_bp.route("/")
def index():
    return render_template("index.html")

@pages_bp.route("/login")
def login():
    return render_template("login.html")

@pages_bp.route("/signup")
def signup():
    return render_template("signup.html")

@pages_bp.route("/list")
def view_list():
    return render_template("list.html")

@pages_bp.route("/review")
def view_review():
    return render_template("review.html")

@pages_bp.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@pages_bp.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")