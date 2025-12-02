import os
import time
import json
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, jsonify

from .ProductForm import ProductForm

products_bp = Blueprint("products", __name__)

@products_bp.route("/reg_product")
def reg_item():
    form = ProductForm()
    return render_template("reg_product.html", form=form)

@products_bp.route("/submit_product_post", methods=['POST'])
def reg_item_submit_post():
    DB = current_app.config["DB"]
    STORAGE = DB.storage

    # 로그인 상태 확인
    seller_id = session.get("id")
    if not seller_id:
        flash("로그인 후에만 상품을 등록할 수 있습니다.")
        return redirect(url_for("pages.login"))

    form = ProductForm()

    # 유효성 검사 및 CSRF 토큰 확인
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for e in errors:
                flash(f"[{field}] {e}")
        return redirect(request.referrer or url_for('products.view_products'))

    files = request.files.getlist("file")
    img_urls = []

    for image_file in files:
        if not image_file or not image_file.filename:
            continue

        original = secure_filename(image_file.filename)
        name, ext = os.path.splitext(original)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

        save_path = f"products/{unique_name}"
        STORAGE.child(save_path).put(image_file)
        url = STORAGE.child(save_path).get_url(None)

        img_urls.append(url)

    img_filename = json.dumps(img_urls) if img_urls else None

    # 폼 데이터
    data = form.data.copy()

    if 'csrf_token' in data:
        del data['csrf_token']
    if 'file' in data:
        del data['file']

    data['tags'] = form.tag.data

    new_product_id = DB.insert_item(
        name=form.name.data,
        data=data,
        img_path=img_filename,
        seller_id=seller_id
    )

    flash("상품이 성공적으로 등록되었습니다.")
    return redirect(url_for("products.view_product", product_id=new_product_id, slug=data['name']))

# 상품 전체조회
@products_bp.route("/products", methods=["GET"])
def view_products():
    DB = current_app.config["DB"]

    current_id = session.get("id")

    category = request.args.get("category", "").strip()

    # 전체 상품 받아오기 + 정렬
    items = DB.get_products()
    items.sort(key=lambda p: p["id"], reverse=True)

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
        img_raw = p.get("img_path", "")

        try:
            images = json.loads(img_raw) if img_raw else []
            if isinstance(images, str):
                images = [images]
        except Exception:
            images = [img_raw] if img_raw else []

        p["img_path"] = images[0] if images else None

        p["is_owner"] = (p.get("seller") == current_id)


    from math import ceil
    page_count = max(1, ceil(total / per_page))

    return render_template("products.html", datas=page_items, page=page, page_count=page_count, total=total, category=category, tag=tag)

# slug => 과제 요구사항 맞추기 위해 추가 (상품 이름)
@products_bp.route("/products/<string:product_id>/<slug>", methods=["GET"])
def view_product(product_id, slug):
    DB = current_app.config["DB"]
    product = DB.get_product(product_id)

    img_raw = product.get("img_path")

    images = []

    # 1) 이미 리스트라면 그대로
    if isinstance(img_raw, list):
        images = img_raw

    # 2) 문자열인 경우 → JSON 리스트인지 검사
    elif isinstance(img_raw, str):
        # ["a.jpg","b.jpg"] 형태라면
        if img_raw.strip().startswith("["):
            try:
                loaded = json.loads(img_raw)
                if isinstance(loaded, list):
                    images = loaded
                else:
                    images = [img_raw]
            except:
                images = [img_raw]
        else:
            # 순수한 "a.jpg" 형태
            images = [img_raw]

    # 3) None인 경우
    else:
        images = []

    # 최종 리스트 세팅
    product["images"] = images

    # 2) 태그 처리 (원래 있던 코드 그대로)
    raw_tags = product.get("tags", "") or ""
    tag_list = [t for t in raw_tags.split() if t]

    # 3) 내가 등록한 글인지 확인 (원래 있던 코드 그대로)
    current_id = session.get("id")
    is_owner = (product.get("seller") == current_id)

    # 4) 템플릿 렌더 (원래 있던 구조 유지)
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
    STORAGE = DB.storage

    product = DB.get_product(product_id)
    current_id = session.get("id")

    # 권한 체크
    if product.get("seller") != current_id: # 이중 체크, fe에서 권한이 없을 경우 버튼이 보이지 않으나 url 접근 막음
        flash("수정 권한이 없습니다")
        return redirect(url_for("products.view_product", product_id=product_id, slug=slug))
    
    form = ProductForm()

    # GET 요청 : 기존 데이터로 폼 채우기
    
    if request.method == "GET":
        form.name.data = product.get("name")
        form.category.data = product.get("category")
        form.price.data = int(product.get("price", 0))
        form.quantity.data = int(product.get("quantity", 1))
        form.details.data = product.get("details")
        form.tag.data = product.get("tags")

        methods = product.get("method")
        
        # 리스트가 아니라 문자열이면 리스트로 감싸기 (가장 단순한 처리)
        if methods and isinstance(methods, str):
            # 혹시 "['...']" 처럼 저장된 문자열이라면 대괄호/따옴표 제거 (ast 없이 단순 문자열 처리)
            cleaned = methods.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            # 콤마로 구분되어 있으면 쪼개기
            if "," in cleaned:
                methods = [m.strip() for m in cleaned.split(",")]
            else:
                methods = [cleaned.strip()]
        elif methods is None:
            methods = []
            
        form.method.data = methods
        
        return render_template("edit_product.html", product=product, product_id=product_id, slug=slug, form=form)

    # if method == POST 유효성 검사 및 업데이트

    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"[{field}] {error}")
        return render_template("edit_product.html", product=product, product_id=product_id, slug=slug, form=form)

     # 이미지 처리 ---------------------------
    existing_images_field = request.form.get("existing_images", "").strip()

    if existing_images_field:
        # 프론트에서 넘어온 "삭제 후 남아 있는 기존 이미지" 목록 사용
        try:
            loaded = json.loads(existing_images_field)
            if isinstance(loaded, list):
                existing_images = loaded
            elif isinstance(loaded, str):
                existing_images = [loaded]
            else:
                existing_images = []
        except Exception:
            existing_images = []
    else:
        # hidden 값이 비어 있으면 DB에 저장된 원래 img_path 사용
        img_raw = product.get("img_path")

        if isinstance(img_raw, list):
            existing_images = img_raw
        elif isinstance(img_raw, str):
            try:
                loaded = json.loads(img_raw)
                if isinstance(loaded, list):
                    existing_images = loaded
                else:
                    existing_images = [img_raw]
            except Exception:
                existing_images = [img_raw]
        else:
            existing_images = []

    # 새로 업로드된 이미지 처리 (기존 코드 그대로)
    new_images = []
    files = request.files.getlist("file")

    for f in files:
        if not f or not f.filename:
            continue

        original = secure_filename(f.filename)
        name, ext = os.path.splitext(original)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

        save_path = f"products/{unique_name}"
        STORAGE.child(save_path).put(f)

        url = STORAGE.child(save_path).get_url(None)
        new_images.append(url)

    # 최종 이미지 리스트 = (남아 있는 기존 이미지) + (새로 업로드한 이미지)
    final_images = existing_images + new_images if new_images else existing_images



    # 데이터 업데이트
    update_data = {
        "name": form.name.data,
        "category": form.category.data,
        "details": form.details.data,
        "price": form.price.data,
        "quantity": form.quantity.data,
        "method": form.method.data, 
        "img_path": json.dumps(final_images),
        "seller": product.get("seller"),
        "tags": form.tag.data
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
    
    # 만약 본인이 판매자라면
    if user_id == product.get("seller",""):
        return jsonify({"success":False,"message":"자신이 등록한 상품은 구매할 수 없습니다."}),400

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