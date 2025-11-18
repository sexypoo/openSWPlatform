import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
# from flask import sys
from database import DBhandler

reviews_bp = Blueprint("reviews",__name__)

@reviews_bp.route("/submit_review")
def reg_item_submit():
    name = request.args.get("name")
    seller = request.args.get("seller")
    addr = request.args.get("addr")
    email = request.args.get("email")
    category = request.args.get("category")
    card = request.args.get("card")
    status = request.args.get("status")
    phone = request.args.get("phone")
    print(name, seller, addr, email, category, card, status, phone)
    return render_template("reg_items.html")

@reviews_bp.route("/submit_review_post", methods=['POST'])
def reg_review_submit_post():
    # 로그인 상태 확인
    purchaser_id = session.get("id")
    if not purchaser_id:
        flash("로그인 후에만 리뷰를 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    # 이미지 파일 저장
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    
    # 폼 데이터 저장
    data = request.form
    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    
    # 로그인된 유저의 정보를 purchaser로 넘김
    new_review_id = DB.insert_review(data['name'], data, image_file.filename, purchaser_id=purchaser_id)
    
    return redirect(url_for("reviews.view_review", review_id=new_review_id))

@reviews_bp.route("/reviews")
def view_reviews():
    DB = current_app.config["DB"]
    page = request.args.get("page", 1, type = int)
    per_page = 6
    reviews = DB.get_reviews()
    total = len(reviews)

    start = (page-1) *  per_page
    end = start + per_page
    page_reviews = reviews[start:end]

    from math import ceil
    page_count = max(1, ceil(total/per_page))

    return render_template("review.html", datas=page_reviews, page=page, page_count=page_count, total=total)

@reviews_bp.route("/reviews/<string:review_id>")
def view_review(review_id):
    DB = current_app.config["DB"]
    review = DB.get_review(review_id)
    if review['rating'] is not None:
        review['rating'] = int(review['rating'])

    # 내가 등록한 리뷰인지 확인
    current_id = session.get("id")
    is_owner = (review.get("purchaser") == current_id)

    return render_template("review_detail.html", review=review, review_id=review_id, is_owner=is_owner)

