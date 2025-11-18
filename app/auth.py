import hashlib
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
# from flask import sys
from database import DBhandler


auth_bp = Blueprint("auth",__name__)

def _hash_pw(pw:str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@auth_bp.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode()).hexdigest()

    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    if DB.insert_user(data, pw_hash):
        return redirect(url_for("pages.login"))
    else:
        flash("user id already exists")
        return redirect(url_for("pages.signup"))

@auth_bp.route("/login_confirm", methods=["POST"])
def login_user():
    id_=request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
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

@auth_bp.route("/user_info")
def get_user_info():
    return render_template("mypage.html")
