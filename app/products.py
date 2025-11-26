import os
import time
import json
from unicodedata import category

from flask import current_app
from requests_toolbelt.multipart.encoder import total_len
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app, jsonify

from database import DBhandler

products_bp = Blueprint("products",__name__)

# 상품 등록 POST
@products_bp.route("/submit_product_post", methods=['POST'])
def reg_item_submit_post():

    # 로그인 상태 확인
    seller_id = session.get("id")
    if not seller_id:
        flash("로그인 후에만 상품을 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    # 이미지 파일 저장
    # 여러 장 파일 받기
    files = request.files.getlist("files")
    filenames = []

    for f in files:
        if f and f.filename:
            filename = secure_filename(f.filename)
            f.save(os.path.join("static/images", filename))
            filenames.append(filename)

    
    # 폼 데이터 저장
    data=request.form
    DB = current_app.config["DB"] # 현재 앱에서 생성된 DB를 가져와서 사용
    
    # 로그인된 유저의 정보를 seller로 넘김
    import json
    new_product_id = DB.insert_item(data['name'], data, json.dumps(filenames), seller_id=seller_id)
    
    return redirect(url_for("products.view_product", product_id=new_product_id, slug=data['name']))

# 상품 전체조회
@products_bp.route("/products", methods=["GET"])
def view_products():
    DB = current_app.config["DB"]

    category = request.args.get("category", "").strip()
    items = DB.get_products()
    tag = request.args.get("tag", "").strip()

    if category: # 카테고리 있으면 받아와서 저장
        items = [p for p in items if p.get("category") == category]

    if tag:
        search_token = "#" + tag
        filtered = []
        for p in items:
            raw_tags = p.get("tags", "") or ""
            if search_token in raw_tags.split():
                filtered.append(p)
        items = filtered

    # 페이지네이션 구현
    page = request.args.get("page", 1, type=int)
    per_page = 6 # 한 페이지에 6개씩 볼 수 있음
    total = len(items)

    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    for p in page_items:
        img_raw = p.get("img_path", "")  # ← 이 줄에서 img_raw를 정의합니다

        try:
            # img_path에 ["a.jpg","b.jpg"] 같은 JSON 문자열이 들어있는 경우
            images = json.loads(img_raw) if img_raw else []
            if isinstance(images, str):   # 단일 문자열인 경우 보정
                images = [images]
        except Exception:
            # JSON 형식이 아니면 예전 데이터(단일 문자열)로 취급
            images = [img_raw] if img_raw else []

        # products.html 썸네일에서는 첫 번째 이미지 한 장만 사용
        p["img_path"] = images[0] if images else None

    for p in page_items:
        img_raw = p.get("img_path", "")

        try:
            images = json.loads(img_raw) if img_raw else []  # JSON → 리스트
            if isinstance(images, str):      # 문자열 하나인 경우 보정
                images = [images]
        except Exception:
            images = [img_raw] if img_raw else []

        p["img_path"] = images[0] if images else None  

    from math import ceil
    page_count = max(1, ceil(total / per_page))

    return render_template("products.html", datas=page_items, page=page, page_count=page_count, total=total, category=category, tag=tag)

# slug => 과제 요구사항 맞추기 위해 추가 (상품 이름)
@products_bp.route("/products/<string:product_id>/<slug>", methods=["GET"])
def view_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)

    # 🔹 1) 이미지 여러 장 처리
    img_raw = product.get("img_path", "")

    try:
        # img_path에 ["a.jpg","b.jpg"] 같은 JSON 문자열이 들어 있는 경우
        images = json.loads(img_raw) if img_raw else []
        # 혹시 단일 문자열이 들어있는 경우 (예: "a.jpg")
        if isinstance(images, str):
            images = [images]
    except Exception:
        # JSON 형식이 아니면 그냥 한 장으로 취급
        images = [img_raw] if img_raw else []

    # 템플릿에서 product.images 로 쓸 수 있게 세팅
    product["images"] = images

    # 🔹 2) 태그 처리 (원래 있던 코드 그대로)
    raw_tags = product.get("tags", "") or ""
    tag_list = [t for t in raw_tags.split() if t]

    # 🔹 3) 내가 등록한 글인지 확인 (원래 있던 코드 그대로)
    current_id = session.get("id")
    is_owner = (product.get("seller") == current_id)

    # 🔹 4) 템플릿 렌더 (원래 있던 구조 유지)
    return render_template(
        "product_detail.html",
        product=product,
        product_id=product_id,
        is_owner=is_owner,
        tag_list=tag_list
    )

@products_bp.route("/products/<string:product_id>/<slug>/edit", methods=['GET', 'POST'])
def edit_product(product_id, slug):
    DB = current_app.config["DB"]

    product = DB.get_product(product_id)
    current_id = session.get("id")

    if product.get("seller") != current_id: # 이중 체크, fe에서 권한이 없을 경우 버튼이 보이지 않으나 url 접근 막음
        flash("수정 권한이 없습니다")
        return redirect(url_for("products.view_product", product_id=product_id, slug=slug))
    
    if request.method == "GET":
        return render_template("edit_product.html", product=product, product_id=product_id, slug=slug)

    # if method == POST
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
        "seller": product.get("seller"),
        "tags": data.get("tag", "")
    }

    DB.update_product(product_id, update_data)

    flash("상품이 수정되었습니다")
    return redirect(url_for("products.view_product", product_id=product_id, slug=slug))


@products_bp.route("/products/<string:product_id>/<slug>/delete", methods=['GET', 'POST'])
def delete_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)
    current_id = session.get("id")

    if product.get("seller") != current_id:
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("products.view_product", product_id=product_id, slug=slug))

    DB.delete_product(product_id)
    flash("상품이 삭제 되었습니다")
    return redirect(url_for("products.view_products"))

# 상품 구매 로직
@products_bp.route("/products/<string:product_id>/<slug>/buy",methods=["POST"])
def buy_product(product_id, slug):
    DB = current_app.config["DB"]
    # 실제 아이디
    user_id = session.get("id")

    # 로그인 여부 확인
    if not user_id:
        flash("로그인 후에만 상품을 구매할 수 있습니다.")
        return redirect(url_for("pages.login"))
    
    # 고유 아이디
    uid = DB.get_uid_by_id(user_id)

    # 상품 정보 조회
    product = DB.get_product(product_id)
    
    # 폼 데이터 받기
    quantity = request.form.get("quantity","1")
    purchaser_name = request.form.get("purchaser_name", "")
    purchaser_contact = request.form.get("purchaser_contact","")
    purchaser_addr = request.form.get("purchaser_addr","")

    # 수량 검증
    try:
        quantity=int(quantity)
    except ValueError:
        return jsonify({"success":False, "message":"수량은 1개 이상이어야 합니다."}),400
    
    if quantity <= 0:
        return jsonify({"success":False,"message":"수량은 1개 이상이어야 합니다."}),400
    
    # 재고 체크
    stock = int(product.get("quantity",0)) # 현재 수량 받아오기
    if quantity > stock:
        return jsonify({"success":False, "message":"재고가 부족합니다."}),400
    
    # 구매 내역 데이터 구성
    purchase_data = {
        "quantity": quantity,
        "purchased_at": int(time.time()),
        "purchaser_id":user_id,
        "purchaser_name":purchaser_name,
        "purchaser_contact":purchaser_contact,
        "purchaser_addr":purchaser_addr
    }

    # DB 저장 (구조 : user/{uid}/purchases/{pid}/{auto_id})
    DB.add_purchase_for_user(uid, product_id, purchase_data)

    # item 재고 차감
    new_stock = stock-quantity
    DB.update_product(product_id, {"quantity": new_stock})

    return jsonify({
        "success":True,
        "message":"구매가 완료되었습니다.",
        "remain_quantity":new_stock
    })