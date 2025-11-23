import hashlib
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
from database import DBhandler

# 로그인/회원가입 등 유저 관리 기능 blueprint
auth_bp = Blueprint("auth",__name__)

# 비밀번호 암호화 함수
def _hash_pw(pw:str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

@auth_bp.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = _hash_pw(pw)

    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    if DB.insert_user(data, pw_hash): # 등록 검증은 DB단에서 실행
        return redirect(url_for("pages.login"))
    else:
        flash("user id already exists")
        return redirect(url_for("pages.signup"))

@auth_bp.route("/login_confirm", methods=["POST"])
def login_user():
    id_=request.form['id']
    pw = request.form['pw']
    pw_hash = _hash_pw(pw)

    DB = current_app.config["DB"]
    if DB.find_user(id_, pw_hash):
        session["id"] = id_
        return redirect(url_for("pages.index"))
    else:
        flash("Wrong ID or Password")
        return redirect(url_for("pages.login"))

@auth_bp.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for("pages.index"))

