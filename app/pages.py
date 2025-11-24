from flask import Blueprint, render_template, current_app

# 엔드포인트별로 페이지 보여줌
pages_bp = Blueprint("pages",__name__)

@pages_bp.route("/")
def index():
    DB = current_app.config["DB"]
    products = DB.get_products()
    reviews = DB.get_reviews()
    latest_products = products[-4:] if len(products) > 4 else products
    latest_reviews = reviews[-4:] if len(reviews) > 4 else reviews
    return render_template("index.html", latest_products=latest_products, latest_reviews=latest_reviews)

@pages_bp.route("/login")
def login():
    return render_template("login.html")

@pages_bp.route("/signup")
def signup():
    return render_template("signup.html")

@pages_bp.route("/product")
def view_list():
    return render_template("products.html")


@pages_bp.route("/review")
def view_review():
    return render_template("review.html")

@pages_bp.route("/reg_items")
def reg_item():
    return render_template("reg_product.html")
