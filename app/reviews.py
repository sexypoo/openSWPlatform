import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
# from flask import sys
from database import DBhandler

reviews_bp = Blueprint("reviews",__name__)

@reviews_bp.route("/get_product",methods=['GET'])
def reg_review_get():
    DB = current_app.config["DB"]

    item_id = request.args.get("item_id")

    item = DB.get_product(item_id) if item_id else None

    return render_template("reg_reviews.html", item=item, item_id=item_id, review=None, review_id=None)


@reviews_bp.route("/reg_reviews")
def reg_review():
    DB = current_app.config["DB"]
    item_id = request.args.get("item_id")
    item = DB.get_product(item_id) if item_id else None

    return render_template(
        "reg_reviews.html",
        review=None,
        item=item,
        item_id=item_id,
        mode="create",
    )

@reviews_bp.route("/submit_review_post", methods=['POST'])
def reg_review_submit_post():
    # 로그인 상태 확인
    purchaser_id = session.get("id")
    if not purchaser_id:
        flash("로그인 후에만 리뷰를 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    # 이미지 파일 저장
    files = request.files.getlist("file")
    img_filenames = []

    for image_file in files[:3]:
        if not image_file or not image_file.filename:
            continue

        filename = secure_filename(image_file.filename)
        save_path = f"static/images/{filename}"

        image_file.save(save_path)
        img_filenames.append(filename)

        
    # 폼 데이터 저장
    data = request.form.to_dict()
    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    
    item_id = data.get("item_id") or None

    # 기본값: 사용자가 폼에 쓴 값
    name = data.get("name", "")
    p_details = data.get("p_details", "")
    seller_id = data.get("seller_id", "")

    # item_id가 있으면 product 값으로 덮어쓰기
    if item_id:
        product = DB.get_product(item_id) or {}
        name = product.get("name", name)
        p_details = product.get("details", p_details)
        seller_id = product.get("seller", seller_id)

    data["p_details"] = p_details
    data["seller_id"] = seller_id

    # 리뷰 저장
    new_review_id = DB.insert_review(
        name=name,
        data=data,
        img_paths=img_filenames,
        purchaser_id=purchaser_id,
        item_id=item_id,
    )
    
    return redirect(url_for("reviews.view_review", review_id=new_review_id))

@reviews_bp.route("/reviews")
def view_reviews():
    DB = current_app.config["DB"]

    # 현재 페이지 받아오기
    page = request.args.get("page", 1, type = int)
    per_page = 6

    # 전체 리뷰 받아오기 + 정렬
    reviews = DB.get_reviews()
    reviews.sort(key=lambda r:r["id"], reverse=True)

    total = len(reviews)

    # 슬라이싱
    start = (page-1) *  per_page
    end = start + per_page
    page_reviews = reviews[start:end]

    # 페이지 개수
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

@reviews_bp.route("/reviews/update/<string:review_id>", methods=["GET","POST"])
def update_review(review_id):
    DB = current_app.config["DB"]
    user_id = session.get("id")

    review = DB.get_review(review_id)
    if not review or review.get("purchaser") != user_id:
        flash("수정 권한이 없습니다.")
        return redirect(url_for("reviews.view_review",review_id=review_id))
    
    if request.method == "POST":
        data = request.form.to_dict()

        update_fields = {
            "title": data.get("title"),
            "review_details": data.get("r_details"),
            "rating": data.get("rating")
        }

        image_file = request.files.get("file")

        if image_file and image_file.filename:
            img_filename = image_file.filename
            image_file.save(f"static/images/{img_filename}")
            update_fields["img_path"] = img_filename

        DB.update_review(review_id, update_fields)
        flash("리뷰가 수정되었습니다.")
        return redirect(url_for("reviews.view_review", review_id=review_id))
    
    item = None
    item_id = review.get("item_id")
    if item_id: # 만약 리뷰와 연결된 상품이 있다면 정보 받아오기
        item = DB.get_product(item_id)
    return render_template(
        "reg_reviews.html",
        review=review,
        review_id=review_id,
        item=item,
        item_id=item_id, # 필요하면 템플릿에서 새 작성/수정 구분용
    )


@reviews_bp.route("/reviews/delete/<string:review_id>")
def delete_review(review_id):
    DB = current_app.config["DB"]
    user_id = session.get("id")

    review = DB.get_review(review_id)
    if not review or review.get("seller") != user_id:
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("reviews.view_review",review_id=review_id))
    
    DB.delete_review(review_id)
    flash("상품이 삭제되었습니다.")
    return redirect(url_for("reviews.view_reviews"))

