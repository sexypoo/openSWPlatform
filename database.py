from operator import truediv

import pyrebase
import json


class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['seller'],
            "addr": data['addr'],
            "email": data['email'],
            "category": data['category'],
            "card": data['card'],
            "status": data['status'],
            "phone": data['phone'],
            "img_path": img_path
        }
        self.db.child('items').child(name).set(item_info)
        print(data, img_path)
        return True

    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "nickname": data['nickname']
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
