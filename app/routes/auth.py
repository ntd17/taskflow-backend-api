from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..models import User
from .. import db

auth_ns = Namespace('auth', description='Authentication related operations')

user_model = auth_ns.model('User', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='User password'),
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return {'message': 'User with that username or email already exists'}, 400

        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {'message': 'Invalid username or password'}, 401

        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, 200
