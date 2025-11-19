from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

from .auth import _hash_pw

user_bp = Blueprint("user", __name__)

@user_bp.route("/mypage", methods=["GET"])
def mypage():
    DB = current_app.config["DB"]
    user_id = session.get("id")

    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))

    user = DB.get_user(user_id)
    heart_ids = DB.get_my_heart_ids(user_id)
    products = DB.get_products_by_ids(heart_ids)
    # reviews = DB.get_user_reviews(user_id)

    return render_template("mypage.html", user=user, products=products)


@user_bp.route("/mypage/update", methods=["POST"])
def update_profile():
    DB = current_app.config["DB"]
    user_id = session.get("id")

    if not user_id:
        flash("로그인이 필요합니다.")
        return redirect(url_for("login"))

    new_password = request.form.get("password_new")
    new_email = request.form.get("email")

    if new_password:
        hashed = _hash_pw(new_password)
        DB.update_user_password(user_id, hashed)
    if new_email:
        DB.update_user_email(user_id, new_email)

    print(new_password,new_email)
    flash("회원정보가 수정되었습니다.")
    return redirect(url_for("user.mypage"))
