from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
api = Api(version='1.0', title='TaskFlow API', description='A Trello-like backend API for TaskFlow')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    # Import and register namespaces (routes)
    from .routes.auth import auth_ns
    from .routes.board import board_ns
    from .routes.list import list_ns
    from .routes.card import card_ns

    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(board_ns, path='/api/boards')
    api.add_namespace(list_ns, path='/api/lists')
    api.add_namespace(card_ns, path='/api/cards')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
