import hashlib
import re
from flask import Blueprint, request, flash, redirect, url_for, session, current_app
from database import DBhandler

auth_bp = Blueprint("auth", __name__)

# 아이디 정규식: 3~20자의 영문/숫자/밑줄
ID_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


@auth_bp.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form

    # 폼에서 넘어오는 실제 name은 'id', 'pw' 라고 가정
    user_id = data.get("id", "").strip()
    pw = data.get("pw", "").strip()

    # 1) 빈 값 체크
    if not user_id or not pw:
        flash("Please fill in all fields")
        return redirect(url_for("pages.signup"))

    # 2) 아이디 형식 체크
    if not ID_PATTERN.match(user_id):
        flash("아이디는 3~20자 사이의 영문, 숫자, 밑줄(_)만 사용할 수 있습니다.")
        return redirect(url_for("pages.signup"))

    pw_hash = _hash_pw(pw)

    DB = current_app.config["DB"]
    if DB.insert_user(data, pw_hash):
        return redirect(url_for("pages.login"))
    else:
        flash("user id already exists")
        return redirect(url_for("pages.signup"))


@auth_bp.route("/login_confirm", methods=["POST"])
def login_user():
    id_ = request.form.get('id', '').strip()
    pw = request.form.get('pw', '').strip()

    if not id_ or not pw:
        flash("ID와 비밀번호를 모두 입력해주세요.")
        return redirect(url_for("pages.login"))

    # 지우지 말아주세요 ID 로그인시 체크하는 함수입니다.
    # if not ID_PATTERN.match(id_):
    #     flash("아이디 형식이 올바르지 않습니다.")
    #     return redirect(url_for("pages.login"))

    pw_hash = _hash_pw(pw)

    DB = current_app.config["DB"]
    if DB.find_user(id_, pw_hash):
        session.clear()
        session["id"] = id_
        return redirect(url_for("pages.index"))
    else:
        flash("Wrong ID or Password")
        return redirect(url_for("pages.login"))


@auth_bp.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for("pages.index"))