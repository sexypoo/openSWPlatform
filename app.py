

from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

@application.route("/")
def hello():
    return render_template("index.html")
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)

@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=["POST"])
def register_user():
    data = request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exists")
        return render_template("signup.html")

# @application.route("/login_post", methods=["POST"])
# def login_user():
#     data = request.form
#     uid = data["id"]
#     pw=data["pw"]
#     pw_hash = hashlib.sha256(pw.encode()).hexdigest()
#
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

@application.route("/list")
def view_list():
    return render_template("list.html")

@application.route("/review")
def view_review():
    return render_template("review.html")

@application.route("/reg_items")
def reg_item():
    return render_template("reg_items.html")

@application.route("/reg_reviews")
def reg_review():
    return render_template("reg_reviews.html")

@application.route("/submit_item")
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

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'], data, image_file.filename)
    # name = request.form.get("name")
    # seller = request.form.get("seller")
    # addr = request.form.get("addr")
    # email = request.form.get("email")
    # category = request.form.get("category")
    # card = request.form.get("card")
    # status = request.form.get("status")
    # phone = request.form.get("phone")
    # print(name, seller, addr, email, category, card, status, phone)
    return render_template("submit_item_result.html", data=data, img_path="static/images/{}".format(image_file.filename))
