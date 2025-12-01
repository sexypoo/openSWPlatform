import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
# from flask import sys
import datetime
from database import DBhandler

from .ReviewForm import ReviewForm

reviews_bp = Blueprint("reviews",__name__)

# 리뷰 등록 case
# 1. 상품 상세조회 -> 리뷰작성 통해 리뷰를 등록하는 경우 : 상품 정보 받아옴
# 2. 일반 작성 : 상품 정보 등록자가 직접 작성
@reviews_bp.route("/reg_reviews")
def reg_review():
    DB = current_app.config["DB"]
    item_id = request.args.get("item_id")
    item = DB.get_product(item_id) if item_id else None

    # Flask-WTF는 form이 실행되는 순간 폼 객체 안에 csrf token을 생성해서 넣음
    form = ReviewForm()

    return render_template(
        "reg_reviews.html",
        form=form,
        review=None,
        item=item,
        item_id=item_id,
        mode="create",
    )

# 리뷰 작성 페이지 불러오기 - 만약 item(상품정보)가 존재한다면 담아서 보냄
@reviews_bp.route("/get_product", methods=['GET'])
def reg_review_get():
    DB = current_app.config["DB"]

    item_id = request.args.get("item_id")
    item = DB.get_product(item_id) if item_id else None

    user_id = session.get("id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("pages.login"))
    
    if item_id:
        uid = DB.get_uid_by_id(user_id) # Firebase 고유 id 변환
        if not DB.has_purchased_product(uid, item_id):
            flash("구매한 상품에만 리뷰를 작성할 수 있습니다.")
            slug = item.get("name", "")
            return redirect(url_for("products.view_product", product_id=item_id, slug=slug))

    # Flask-WTF는 form이 실행되는 순간 폼 객체 안에 csrf token을 생성해서 넣음
    form = ReviewForm()

    return render_template("reg_reviews.html", item=item, item_id=item_id, review=None, review_id=None, form=form)

# 리뷰 작성
@reviews_bp.route("/submit_review_post", methods=['POST'])
def reg_review_submit_post():
    
    # 구매자 id (본인) 받아오기
    purchaser_id = session.get("id")

    # 로그인 상태 확인
    if not purchaser_id:
        flash("로그인 후에만 리뷰를 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    form = ReviewForm()

    # CSRF + 필드 입력값 검증
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for e in errors:
                flash(f"{field}: {e}")
        
        return redirect(request.referrer)

    # 이미지 파일 저장 : 총 3장 저장 가능
    DB = current_app.config["DB"]
    STORAGE = DB.storage

    files = request.files.getlist("file")
    img_filenames = []

    for image_file in files[:3]:
        if not image_file or not image_file.filename:
            continue

        original = secure_filename(image_file.filename)
        name, ext = os.path.splitext(original)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

        save_path = f"reviews/{unique_name}"
        STORAGE.child(save_path).put(image_file)
        url = STORAGE.child(save_path).get_url(None)

        img_filenames.append(url)
        
    # 폼 데이터 저장

    # 위에서 검증 완료한 form 복사해오기
    data = form.data.copy()
    data.pop('csrf_token', None) # csrf 토큰은 삭제

    # DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    
    # 상품 id 받아오기
    item_id = data.get("item_id") or None

    # 기본값: 사용자가 폼에 쓴 값
    name = form.name.data or ""
    p_details = form.p_details.data or ""
    seller_id = form.seller.data or ""

    # item_id가 있으면, 저장할 data의 product를 product 값으로 덮어쓰기
    if item_id:
        product = DB.get_product(item_id) or {}
        name = product.get("name", name)
        p_details = product.get("details", p_details)
        seller_id = product.get("seller", seller_id)

    data = {
        "title": form.title.data,
        "r_details": form.r_details.data,
        "rating": form.rating.data,
        "p_details": p_details,
        "seller_id": seller_id,
        "name": name,
    }

    # 리뷰 저장
    new_review_id = DB.insert_review(
        name=name,
        data=data,
        img_paths=img_filenames,
        purchaser_id=purchaser_id,
        item_id=item_id,
    )
    
    flash("리뷰가 성공적으로 등록되었습니다.")
    return redirect(url_for("reviews.view_review", review_id=new_review_id))

# 리뷰 전체조회
@reviews_bp.route("/reviews")
def view_reviews():
    DB = current_app.config["DB"]

    # 현재 페이지 받아오기
    page = request.args.get("page", 1, type = int)
    per_page = 6

    # 전체 리뷰 받아오기 + 정렬
    reviews = DB.get_reviews()
    reviews.sort(key=lambda r:r["id"], reverse=True)

    for r in reviews:
        if "created_at" in r:
            r["created_at_str"] = datetime.datetime.fromtimestamp(
                r["created_at"]
            ).strftime("%Y-%m-%d %H:%M")

    total = len(reviews)

    # 슬라이싱
    start = (page-1) *  per_page
    end = start + per_page
    page_reviews = reviews[start:end]

    # 페이지 개수
    from math import ceil
    page_count = max(1, ceil(total/per_page))

    return render_template("review.html", datas=page_reviews, page=page, page_count=page_count, total=total)

# 리뷰 상세조회
@reviews_bp.route("/reviews/<string:review_id>")
def view_review(review_id):
    DB = current_app.config["DB"]
    review = DB.get_review(review_id)

    if "created_at" in review:
        review["created_at_str"] = datetime.datetime.fromtimestamp(review["created_at"]).strftime("%Y-%m-%d %H:%M")

    # 별점을 정수로 변환
    if review['rating'] is not None:
        review['rating'] = int(review['rating'])

    raw = review.get("images")

    if isinstance(raw, list):
        images = raw
    elif isinstance(raw, str) and raw:  # 혹시 문자열 하나만 들어있는 경우
        images = [raw]
    else:
        images = []

    review["images"] = images

    # 내가 등록한 리뷰인지 확인
    current_id = session.get("id")
    is_owner = (review.get("purchaser") == current_id)

    return render_template("review_detail.html", review=review, review_id=review_id, is_owner=is_owner)

# 리뷰 수정
@reviews_bp.route("/reviews/update/<string:review_id>", methods=["GET","POST"])
def update_review(review_id):

    DB = current_app.config["DB"]
    user_id = session.get("id")

    review = DB.get_review(review_id)
    if not review or review.get("purchaser") != user_id: # 구매자 정보와 본인 id가 일치해야만 수정 가능 (url 수정 방어)
        flash("수정 권한이 없습니다.")
        return redirect(url_for("reviews.view_review",review_id=review_id))

    if not review.get("images"):
        review["images"] = []

    if request.method == "POST":
        form = ReviewForm()

        if not form.validate_on_submit():
            for field, errors in form.errors.items():
                for e in errors:
                    flash(f"{field}: {e}")
            return redirect(request.referrer or url_for("reviews.update_review", review_id=review_id))

        update_fields = {
            "title": form.title.data,
            "review_details": form.r_details.data,
            "rating": form.rating.data,
        }

        DB = current_app.config["DB"]
        STORAGE = DB.storage

        files = request.files.getlist("file")

        # Load existing images list (default empty list)
        existing_images = review.get("images") or []
        new_images = []

        # Process newly uploaded files (multiple)
        for image_file in files:
            if not image_file or not image_file.filename:
                continue
            original = secure_filename(image_file.filename)
            name, ext = os.path.splitext(original)
            unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

            save_path = f"reviews/{unique_name}"
            STORAGE.child(save_path).put(image_file)
            url = STORAGE.child(save_path).get_url(None)

            new_images.append(url)

        # Merge existing + new images
        merged = existing_images + new_images

        # Keep only last 3 images (remove from front)
        if len(merged) > 3:
            merged = merged[-3:]

        update_fields["images"] = merged

        DB.update_review(review_id, update_fields)

        flash("리뷰가 수정되었습니다.")
        return redirect(url_for("reviews.view_review", review_id=review_id))
    
    item = None
    item_id = review.get("item_id")
    item = DB.get_product(item_id) if item_id else None

    form = ReviewForm()

    # 기존 데이터 채워넣기
    form.title.data = review.get("title")
    form.r_details.data = review.get("review_details")
    form.rating.data = review.get("rating")
    form.item_id.data = item_id

    return render_template(
        "reg_reviews.html",
        form=form,
        review=review,
        review_id=review_id,
        item=item,
        item_id=item_id
    )

# 리뷰 삭제
@reviews_bp.route("/reviews/delete/<string:review_id>")
def delete_review(review_id):
    DB = current_app.config["DB"]
    user_id = session.get("id")

    review = DB.get_review(review_id)
    if not review or review.get("purchaser") != user_id:
        
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("reviews.view_review",review_id=review_id))
    
    DB.delete_review(review_id)
    flash("리뷰가 삭제되었습니다.")
    return redirect(url_for("reviews.view_reviews"))

