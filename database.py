from operator import truediv

import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    # item 핸들러

    def insert_item(self, name, data, img_path, seller_id):
        item_info = {
            "name" : name,
            "seller": seller_id,
            "category": data['category'],
            "details": data['details'],
            "price": data["price"],
            "quantity": data.get("quantity", 1),
            "method":(data.getlist("method") if hasattr(data, "getlist") else data.get("method",[])),
            "img_path": img_path,
            "tags": data.get("tag","")

            # "addr": data['addr'],
            # "email": data['email'],
            # "card": data['card'],
            # "status": data['status'],
            # "phone": data['phone'],
        }

        res = self.db.child("items").push(item_info)
        new_id = res['name']

        print(data, img_path, "new_id=", new_id)
        return new_id
    
    def get_products(self):
        raw = self.db.child("items").get().val() or {}
        products = []
        for pid, v in raw.items():
            v = v or {}
            v["id"] = pid
            products.append(v)
        return products

    def get_product(self, product_id):
        data = self.db.child("items").child(product_id).get().val() or {}
        if data:
            data["id"] = product_id

        return data

    def update_product(self, product_id, data):
        self.db.child("items").child(product_id).update(data)

    def delete_product(self, product_id):
        self.db.child("items").child(product_id).remove()

    # 구매 내역 저장
    def add_purchase_for_user(self, user_id, product_id, purchase_info):
        ref = (
            self.db.child("user")
            .child(user_id)
            .child("purchases")
            .child(product_id)
            .push(purchase_info)
        )

        return ref["name"] # name : auto id
    
    # 구매 내역 불러오기
    def get_purchases_by_user(self, uid):
        raw = (
            self.db.child("user")
            .child(uid)
            .child("purchases")
            .get().val()
        ) or {}

        results = []

        for product_id, purchase_map in raw.items():
            if not isinstance(purchase_map, dict):
                continue
            
            # 상품 정보 먼저 가져오기
            product = self.get_product(product_id) or {}

            for purchase_id, info in purchase_map.items():
                if not isinstance(info, dict):
                    continue

                merged = {
                    # 구매 정보
                    "purchase_id": purchase_id,
                    "quantity": info.get("quantity"),
                    "purchase_time": info.get("purchase_time"),

                    # 상품 정보
                    "product_id": product_id,
                    "name": product.get("name"),
                    "price": product.get("price"),
                    "details": product.get("details"),
                    "img_path": product.get("img_path"),
                }

                results.append(merged)

        return results

    # auth 핸들러

    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "nickname": data['nickname'],
            "email": data['email']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print(data)
            return True
        else:
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        print("users###", users.val())
        if users is None or str(users.val()) is None:
            return True

        for res in (users.each() or []):
            value = res.val()
            if value['id'] == id_string:
                return False
        return True

    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        taget_value=[]
        for res in (users.each() or []):
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False
    
    def get_uid_by_id(self, user_id:str):
        snap = self.db.child("user").get().val() or {}

        for uid, info in snap.items():
            if not isinstance(info, dict):
                continue
            if info.get("id") == user_id:
                return uid
        
        return None
    
    # review 핸들러
    
    # Create
    def insert_review(self, name, data, img_paths, purchaser_id, item_id=None):
        review_info = {
            "name" : name,
            "title" : data['title'],
            "seller": data['seller_id'],
            "purchaser": purchaser_id,
            "product_details": data['p_details'],
            "review_details": data['r_details'],
            "rating": data['rating'],
            "images": img_paths,
            "item_id": item_id
        }

        res = self.db.child("reviews").push(review_info)
        new_id = res['name']

        return new_id
    
    # Read all
    def get_reviews(self):
        raw = self.db.child("reviews").get().val() or {}
        reviews = []
        for rid, v in raw.items():
            v = v or {}
            v["id"] = rid
            reviews.append(v)
        return reviews
    
    # Read One
    def get_review(self, review_id):
        data = self.db.child("reviews").child(review_id).get().val() or {}
        if data:
            data["id"] = review_id
        return data
    
    # Update
    def update_review(self, review_id, data):
        self.db.child("reviews").child(review_id).update(data)

    # Delete
    def delete_review(self, review_id):
        self.db.child("reviews").child(review_id).remove()

    def has_purchased_product(self, uid, product_id):

        data = (
            self.db.child("user")
            .child(uid)
            .child("purchases")
            .child(product_id)
            .get()
            .val()
        )
        return bool(data)

    # wish 핸들러

    def get_heart_byid(self, uid, id):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""
        if hearts.val() == None:
            return target_value
        
        for res in hearts.each():
            key_value = res.key()

            if key_value == id:
                target_value = res.val()

        return target_value
    
    def update_heart(self, uid, isHeart, item):
        heart_info = {
            "interested" : isHeart
        }
        self.db.child("heart").child(uid).child(item).set(heart_info)
        return True
    
    def get_my_heart_ids(self,uid):
        mywish = self.db.child("heart").child(uid).get()

        if not mywish.each():
            return []
        
        ids = []
        for node in mywish.each():
            data = node.val()
            if isinstance(data,dict) and data.get("interested") == "Y":
                ids.append(node.key())
        return ids
    
    def get_products_by_ids(self,id_list):
        all_products = self.get_products()
        id_set = set(id_list) # 검색 속도 향상
        products = [p for p in all_products if p.get("id") in id_set]
        return products
    
    def get_items_by_seller(self,seller_id):
        sell_items = self.db.child("items").order_by_child("seller").equal_to(seller_id).get()
        items = []

        for node in (sell_items.each() or []):
            v = node.val() or {}
            v["id"] = node.key()
            items.append(v)

        return items
    
    def get_reviews_by_purchaser(self,purchaser_id):
        review_items = self.db.child("reviews").order_by_child("purchaser").equal_to(purchaser_id).get()
        reviews = []

        for node in (review_items.each() or []):
            v = node.val() or {}
            v["id"] = node.key()
            reviews.append(v)

        return reviews


    # User Handler

    def get_user(self, user_id: str):
        users = self.db.child("user").get()

        if not users or users.val() is None:
            return None
        
        for res in (users.each() or []):
            value = res.val() or {}
            if value.get("id") == user_id:
                user_data = value.copy()
                user_data["_key"] = res.key()
                return user_data
        
        return None
    
    def update_user_password(self, user_id:str, new_password:str):
        users = self.db.child("user").get()

        if not users or users.val() is None:
            return False
        
        for res in (users.each() or []):
            value = res.val() or {}
            if str(value.get("id")) == str(user_id):
                key = res.key()
                self.db.child("user").child(key).update({"pw":new_password})
                print(new_password)

                return True
        return False
    
    def update_user_email(self, user_id:str, new_email:str):
        users = self.db.child("user").get()

        if not users or users.val() is None:
            return False
        
        for res in (users.each() or []):
            value = res.val() or {}
            if str(value.get("id")) == str(user_id):
                key = res.key()
                self.db.child("user").child(key).update({"email":new_email})
                return True
        return False