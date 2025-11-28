import json
from flask import Blueprint, render_template, current_app
# 엔드포인트별로 페이지 보여줌
pages_bp = Blueprint("pages",__name__)

@pages_bp.route("/")
def index():
    DB = current_app.config["DB"]
    products = DB.get_products()
    reviews = DB.get_reviews()
    latest_products = products[-4:] if len(products) > 4 else products
    for p in latest_products:
        img_raw = p.get("img_path", "")

        try:
            # img_path에 ["a.jpg","b.jpg"] 같은 JSON 문자열이 들어있는 경우
            images = json.loads(img_raw) if img_raw else []
            if isinstance(images, str):
                images = [images]  # 문자열 하나면 리스트로 감싸기
        except Exception:
            # JSON 형식이 아니면 예전(단일 문자열) 데이터로 취급
            images = [img_raw] if img_raw else []

        # 홈 화면 썸네일에서는 첫 번째 이미지만 사용
        p["img_path"] = images[0] if images else None
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

