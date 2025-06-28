from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Board, List
from .. import db

list_ns = Namespace('lists', description='List/Column related operations')

list_model = list_ns.model('List', {
    'id': fields.Integer,
    'title': fields.String,
    'board_id': fields.Integer,
    'position': fields.Integer,
})

list_create_model = list_ns.model('ListCreate', {
    'title': fields.String(required=True, description='List title'),
    'position': fields.Integer(required=False, description='Position of the list'),
})

@list_ns.route('/<int:list_id>')
class ListDetail(Resource):
    @jwt_required()
    @list_ns.marshal_with(list_model)
    def get(self, list_id):
        list_obj = List.query.get_or_404(list_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in list_obj.board.members]:
            list_ns.abort(403, 'Access denied')
        return list_obj

    @jwt_required()
    @list_ns.expect(list_create_model)
    @list_ns.marshal_with(list_model)
    def put(self, list_id):
        list_obj = List.query.get_or_404(list_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in list_obj.board.members]:
            list_ns.abort(403, 'Access denied')
        data = request.json
        title = data.get('title')
        position = data.get('position')
        if title:
            list_obj.title = title
        if position is not None:
            list_obj.position = position
        db.session.commit()
        return list_obj

    @jwt_required()
    def delete(self, list_id):
        list_obj = List.query.get_or_404(list_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in list_obj.board.members]:
            list_ns.abort(403, 'Access denied')
        db.session.delete(list_obj)
        db.session.commit()
        return {'message': 'List deleted'}, 200

@list_ns.route('/board/<int:board_id>/lists')
class ListCreate(Resource):
    @jwt_required()
    @list_ns.expect(list_create_model)
    @list_ns.marshal_with(list_model, code=201)
    def post(self, board_id):
        user_id = get_jwt_identity()
        board = Board.query.get_or_404(board_id)
        if user_id not in [member.id for member in board.members]:
            list_ns.abort(403, 'Access denied')
        data = request.json
        title = data.get('title')
        position = data.get('position', 0)
        if not title:
            list_ns.abort(400, 'Title is required')
        new_list = List(title=title, board_id=board_id, position=position)
        db.session.add(new_list)
        db.session.commit()
        return new_list, 201
