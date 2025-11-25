from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import re
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
    elif section == "sell":
        my_items = DB.get_items_by_seller(user_id)
    elif section == "buy":
        uid = DB.get_uid_by_id(user_id)
        my_buys = DB.get_purchases_by_user(uid)
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

