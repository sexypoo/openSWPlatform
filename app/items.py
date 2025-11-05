import os
from flask import Blueprint, request, render_template
from flask import current_app
from werkzeug.utils import secure_filename

items_bp = Blueprint("items",__name__)

@items_bp.route("/submit_item")
def reg_item_submit():
    # 원본 GET 로직 그대로 유지
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

@items_bp.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    
    data=request.form
    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    DB.insert_item(data['name'], data, image_file.filename)
    
    return render_template("submit_item_result.html",
                           data=data,
                           img_path="static/images/{}".format(image_file.filename))
