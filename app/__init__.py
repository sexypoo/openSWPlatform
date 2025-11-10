import os
from flask import Flask
from database import DBhandler

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    app.config["SECRET_KEY"] = "helloosp"
    app.config["ALLOWED_EXTS"] = {"png", "jpg", "jpeg", "gif", "webp"}

    # DB 인스턴스 한 번만 생성해서 공유
    app.config["DB"] = DBhandler()

    # 블루프린트 등록
    from .pages import pages_bp
    from .auth import auth_bp
    from .items import items_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)

    return app