from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restx import Api
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
api = Api(version='1.0', title='TaskFlow API', description='A Trello-like backend API for TaskFlow')

def create_app():
    # Create and configure the Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    # Import and register namespaces (routes)
    with app.app_context():
        from app.routes.auth import auth_ns
        from app.routes.board import board_ns
        from app.routes.list import list_ns
        from app.routes.card import card_ns

        api.add_namespace(auth_ns, path='/api/auth')
        api.add_namespace(board_ns, path='/api/boards')
        api.add_namespace(list_ns, path='/api/lists')
        api.add_namespace(card_ns, path='/api/cards')

    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
