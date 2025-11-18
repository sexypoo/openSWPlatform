import os
from crypt import methods

from flask import current_app
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app
from flask import current_app
# from flask import sys
from database import DBhandler

items_bp = Blueprint("items",__name__)

@items_bp.route("/submit_item")
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

@items_bp.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():

    # 로그인 상태 확인
    seller_id = session.get("id")
    if not seller_id:
        flash("로그인 후에만 상품을 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    # 이미지 파일 저장
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    
    # 폼 데이터 저장
    data=request.form
    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    
    # 로그인된 유저의 정보를 seller로 넘김
    new_product_id = DB.insert_item(data['name'], data, image_file.filename, seller_id=seller_id)
    
    return redirect(url_for("items.view_product", product_id=new_product_id, slug=data['name']))

@items_bp.route("/products")
def view_products():
    DB = current_app.config["DB"]
    page = request.args.get("page", 1, type=int)
    per_page = 6
    items = DB.get_products()
    total = len(items)

    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]

    from math import ceil
    page_count = max(1, ceil(total / per_page))

    return render_template("products.html", datas=page_items, page=page, page_count=page_count, total=total)

@items_bp.route("/products/<string:product_id>/<slug>")
def view_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)

    # 내가 등록한 글인지 확인
    current_id = session.get("id")
    is_owner = (product.get("seller") == current_id)

    return render_template("product_detail.html", product=product, product_id=product_id, is_owner=is_owner)


@items_bp.route("/products/<string:product_id>/<slug>/edit", methods=['GET', 'POST'])
def edit_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)
    current_id = session.get("id")
    if product.get("seller") != current_id:
        flash("수정 권한이 없습니다")
        return redirect(url_for("items.view_product", product_id=product_id, slug=slug))
    if request.method == "GET":
        return render_template("edit_product.html", product=product, product_id=product_id, slug=slug)

    data = request.form
    image_file = request.files.get("file")
    file_name = product.get("img_path")

    if image_file and image_file.filename:
        file_name = secure_filename(image_file.filename)
        image_file.save("static/images/{}".format(image_file.filename))

    methods = data.getlist("method") if hasattr(data, "getlist") else data.get("method", [])
    update_data = {
        "name": data["name"],
        "category": data["category"],
        "details": data["details"],
        "price": data["price"],
        "quantity": data["quantity"],
        "method": methods,
        "img_path": file_name,
        "seller": product.get("seller")
    }

    DB.update_product(product_id, update_data)
    flash("상품이 수정되었습니다")
    return redirect(url_for("items.view_product", product_id=product_id, slug=slug))


@items_bp.route("/products/<string:product_id>/<slug>/delete", methods=['GET', 'POST'])
def delete_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)
    current_id = session.get("id")

    if product.get("seller") != current_id:
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("items.view_product", product_id=product_id, slug=slug))

    DB.delete_product(product_id)
    flash("상품이 삭제 되었습니다")
    return redirect(url_for("items.view_products"))



