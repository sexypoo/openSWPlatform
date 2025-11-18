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
            "img_path": img_path

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
        return self.db.child("items").child(product_id).get().val() or {}

    def update_product(self, product_id, data):
        self.db.child("items").child(product_id).update(data)

    def delete_product(self, product_id):
        self.db.child("items").child(product_id).remove()

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
    
    # review 핸들러
    
    def insert_review(self, name, data, img_path, purchaser_id):
        review_info = {
            "name" : name,
            "title" : data['title'],
            "seller": data['seller_id'],
            "purchaser": purchaser_id,
            "product_details": data['p_details'],
            "review_details": data['r_details'],
            "rating": data['rating'],
            "img_path": img_path
        }

        res = self.db.child("reviews").push(review_info)
        new_id = res['name']

        print(data, img_path, "new_id=", new_id)
        return new_id
    
    def get_reviews(self):
        raw = self.db.child("reviews").get().val() or {}
        reviews = []
        for rid, v in raw.items():
            v = v or {}
            v["id"] = rid
            reviews.append(v)
        return reviews
    
    def get_review(self, review_id):
        return self.db.child("reviews").child(review_id).get().val() or {}
    