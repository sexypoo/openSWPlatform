import hashlib
from flask import Blueprint, request, render_template, flash
from flask import current_app

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
        return render_template("login.html")
    else:
        flash("user id already exists")
        return render_template("signup.html")

# @auth_bp.route("/login_post", methods=["POST"])
# def login_user():
#     data = request.form
#     uid = data["id"]
#     pw = data["pw"]
#     pw_hash = hashlib.sha256(pw.encode()).hexdigest()
#
#     DB = current_app.config["DB"]  # ← 동일하게 DB 받아옴
#     users = DB.db.child("user").get()
#
#     if not users or users.val() is None:
#         flash("user id does not exist")
#         return render_template("login.html")
#     for res in (users.each() or []):
#         value = res.val()
#         if value['id'] == uid and value['pw'] == pw_hash:
#             session['id'] = uid
#             flash("logged in successfully")
#             return render_template("index.html")
#     flash("login failed")
#     return render_template("login.html")