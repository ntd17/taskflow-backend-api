from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Board, List, Card, UserBoard
from .. import db

board_ns = Namespace('boards', description='Board related operations')

member_model = board_ns.model('Member', {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
})

card_model = board_ns.model('Card', {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'position': fields.Integer,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
})

list_model = board_ns.model('List', {
    'id': fields.Integer,
    'title': fields.String,
    'position': fields.Integer,
    'cards': fields.List(fields.Nested(card_model)),
})

board_model = board_ns.model('Board', {
    'id': fields.Integer,
    'title': fields.String,
    'created_at': fields.DateTime,
    'lists': fields.List(fields.Nested(list_model)),
    'members': fields.List(fields.Nested(member_model)),
})

board_create_model = board_ns.model('BoardCreate', {
    'title': fields.String(required=True, description='Board title'),
})

invite_model = board_ns.model('Invite', {
    'email_or_username': fields.String(required=True, description='Email or username to invite'),
})

@board_ns.route('')
class BoardList(Resource):
    @jwt_required()
    @board_ns.marshal_list_with(board_model)
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return user.boards

    @jwt_required()
    @board_ns.expect(board_create_model)
    @board_ns.marshal_with(board_model, code=201)
    def post(self):
        user_id = get_jwt_identity()
        data = request.json
        title = data.get('title')
        if not title:
            board_ns.abort(400, 'Title is required')
        board = Board(title=title)
        db.session.add(board)
        db.session.commit()
        # Add creator as member
        user_board = UserBoard(user_id=user_id, board_id=board.id)
        db.session.add(user_board)
        db.session.commit()
        return board, 201

@board_ns.route('/<int:board_id>')
class BoardDetail(Resource):
    @jwt_required()
    @board_ns.marshal_with(board_model)
    def get(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        return board

    @jwt_required()
    @board_ns.expect(board_create_model)
    @board_ns.marshal_with(board_model)
    def put(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        data = request.json
        title = data.get('title')
        if title:
            board.title = title
            db.session.commit()
        return board

    @jwt_required()
    def delete(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        db.session.delete(board)
        db.session.commit()
        return {'message': 'Board deleted'}, 200

@board_ns.route('/<int:board_id>/invite')
class BoardInvite(Resource):
    @jwt_required()
    @board_ns.expect(invite_model)
    def post(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        data = request.json
        email_or_username = data.get('email_or_username')
        if not email_or_username:
            board_ns.abort(400, 'Email or username is required')
        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        if not user:
            return {'message': 'User not found'}, 404
        if user in board.members:
            return {'message': 'User already a member'}, 400
        user_board = UserBoard(user_id=user.id, board_id=board.id)
        db.session.add(user_board)
        db.session.commit()
        return {'message': f'User {user.username} invited to board'}, 200

@board_ns.route('/<int:board_id>/members')
class BoardMembers(Resource):
    @jwt_required()
    def post(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        data = request.json
        email = data.get('email')
        if not email:
            board_ns.abort(400, 'Email is required')
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
        if user in board.members:
            return {'message': 'User already a member'}, 400
        user_board = UserBoard(user_id=user.id, board_id=board.id)
        db.session.add(user_board)
        db.session.commit()
        return {'message': f'User {user.username} added to board'}, 200

@board_ns.route('/<int:board_id>/members/<int:user_id>')
class BoardMember(Resource):
    @jwt_required()
    def delete(self, board_id, user_id):
        current_user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if current_user_id not in [member.id for member in board.members]:
            board_ns.abort(403, 'Access denied')
        user_board = UserBoard.query.filter_by(user_id=user_id, board_id=board_id).first()
        if not user_board:
            return {'message': 'User is not a member of the board'}, 404
        db.session.delete(user_board)
        db.session.commit()
        return {'message': 'User removed from board'}, 200
