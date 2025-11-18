import hashlib
from flask import Blueprint
from flask import request, render_template, flash, redirect, url_for
from flask import session
from flask import current_app
from flask import jsonify

from database import DBhandler

wish_bp = Blueprint("wish",__name__)

@wish_bp.route('/show_heart/<string:id>/', methods=['GET'])
def show_heart(id):
    DB = current_app.config["DB"]
    uid = session.get('id')
    if not uid:
        return jsonify({'my_heart':{}})
    
    my_heart = DB.get_heart_byid(session['id'], id)
    return jsonify({'my_heart':my_heart})

@wish_bp.route('/like/<string:id>/', methods=['POST'])
def like(id):
    DB = current_app.config["DB"]
    uid = session.get('id')
    if not uid:
        return jsonify({'msg':'로그인이 필요합니다.'})
    
    DB.update_heart(session['id'], 'Y', id)
    return jsonify({'msg': '위시 등록 완료!'})

@wish_bp.route('/unlike/<string:id>/', methods=['POST'])
def unlike(id):
    DB = current_app.config["DB"]
    uid = session.get('id')
    if not uid:
        return jsonify({'msg':'로그인이 필요합니다.'})
    
    DB.update_heart(session['id'], 'N', id)
    return jsonify({'msg': '위시 등록 해제'})