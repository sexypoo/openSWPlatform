from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
import re
import json
from .auth import _hash_pw

# 마이페이지의 기능을 다룸

user_bp = Blueprint("user", __name__)

PW_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,64}$")

@user_bp.route("/mypage/")
@user_bp.route("/mypage/<string:section>")
def mypage(section="profile"):
    DB = current_app.config["DB"]

    user_id = session.get("id")
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("pages.login"))

    # 공통으로 가져올 것 (유저 정보)
    user = DB.get_user(user_id)

    # 기본 None으로 놓고, 섹션에 따라 필요한 것만 채우기
    wishlist = None
    my_reviews = None
    my_items = None
    my_buys = None

    if section == "wishlist":
        heart_ids = DB.get_my_heart_ids(user_id)
        wishlist = DB.get_products_by_ids(heart_ids)
    elif section == "review":
        my_reviews = DB.get_reviews_by_purchaser(user_id)
        my_reviews = sorted(my_reviews, key=lambda r: r.get("created_at",0),reverse=True)
    elif section == "sell":
        my_items = DB.get_items_by_seller(user_id)

        for p in my_items:
            img_raw = p.get("img_path", "")

            try:
                images = json.loads(img_raw) if img_raw else []
                if isinstance(images, str):
                    images = [images]
            except Exception:
                images = [img_raw] if img_raw else []

            p["img_path"] = images[0] if images else None

    elif section == "buy":
        uid = DB.get_uid_by_id(user_id)
        my_buys = DB.get_purchases_by_user(uid)

        for p in my_buys:
            img_raw = p.get("img_path", "")

            try:
                images = json.loads(img_raw) if img_raw else []
                if isinstance(images, str):
                    images = [images]
            except Exception:
                images = [img_raw] if img_raw else []

            p["img_path"] = images[0] if images else None
            
    else:
        # 예외 섹션 들어오면 profile로 보내기
        section = "profile"

    return render_template(
        "mypage.html",
        user=user,
        wishlist=wishlist,
        review_list=my_reviews,
        sold_list=my_items,
        buy_list=my_buys,
        active_section=section,
    )

# 회원정보 수정
@user_bp.route("/mypage/update", methods=["POST"])
def update_profile():
    DB = current_app.config["DB"]
    user_id = session.get("id")

    # 로그인 검증
    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("login"))

    # form에서 변경할 비밀번호와 email 받아옴
    new_password = request.form.get("password_new")
    new_email = request.form.get("email")

    if new_password:
        if not PW_PATTERN.match(new_password):
            flash("비밀번호는 8자 이상이어야 하고, 영문과 숫자를 각각 최소 1자 이상 포함해야 합니다.")
            return redirect(url_for("user.mypage", section="profile"))
        
        hashed = _hash_pw(new_password) # 암호화 후 전달
        DB.update_user_password(user_id, hashed)
        
    if new_email:
        DB.update_user_email(user_id, new_email)

    flash("회원정보가 수정되었습니다.")
    return redirect(url_for("user.mypage"))

@user_bp.route("/check_password_match", methods=["POST"])
def check_password_match():
    data = request.get_json()
    input_password = data.get("password")
    
    user_id = session.get("id")
    if not user_id or not input_password:
        return jsonify({"match": False}) # 로그인 안됐거나 입력 없으면 불일치 처리

    DB = current_app.config["DB"]
    
    # 1. DB에서 현재 유저 정보 가져오기
    current_user = DB.get_user(user_id)
    if not current_user:
        return jsonify({"match": False})

    # 2. 입력된 비밀번호 암호화 (기존 _hash_pw 함수 사용)
    # user.py 상단에 from .auth import _hash_pw 가 되어있어야 함
    hashed_input = _hash_pw(input_password)
    
    # 3. DB 비밀번호와 비교
    current_db_password = current_user.get("pw")
    
    if hashed_input == current_db_password:
        return jsonify({"match": True})  # "똑같습니다!"
    else:
        return jsonify({"match": False}) # "다릅니다!"