from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Board, List, Card
from .. import db

card_ns = Namespace('cards', description='Card related operations')

card_model = card_ns.model('Card', {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'list_id': fields.Integer,
    'position': fields.Integer,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
})

card_create_model = card_ns.model('CardCreate', {
    'title': fields.String(required=True, description='Card title'),
    'description': fields.String(required=False, description='Card description'),
    'position': fields.Integer(required=False, description='Position of the card'),
})

card_move_model = card_ns.model('CardMove', {
    'list_id': fields.Integer(required=True, description='Target list ID'),
    'position': fields.Integer(required=True, description='Target position in the list'),
})

@card_ns.route('/<int:card_id>')
class CardDetail(Resource):
    @jwt_required()
    @card_ns.marshal_with(card_model)
    def get(self, card_id):
        card = Card.query.get_or_404(card_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in card.list.board.members]:
            card_ns.abort(403, 'Access denied')
        return card

    @jwt_required()
    @card_ns.expect(card_create_model)
    @card_ns.marshal_with(card_model)
    def put(self, card_id):
        card = Card.query.get_or_404(card_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in card.list.board.members]:
            card_ns.abort(403, 'Access denied')
        data = request.json
        title = data.get('title')
        description = data.get('description')
        position = data.get('position')
        if title:
            card.title = title
        if description is not None:
            card.description = description
        if position is not None:
            card.position = position
        db.session.commit()
        return card

    @jwt_required()
    def delete(self, card_id):
        card = Card.query.get_or_404(card_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in card.list.board.members]:
            card_ns.abort(403, 'Access denied')
        db.session.delete(card)
        db.session.commit()
        return {'message': 'Card deleted'}, 200

@card_ns.route('/list/<int:list_id>/cards')
class CardCreate(Resource):
    @jwt_required()
    @card_ns.expect(card_create_model)
    @card_ns.marshal_with(card_model, code=201)
    def post(self, list_id):
        user_id = get_jwt_identity()
        list_obj = List.query.get_or_404(list_id)
        if user_id not in [member.id for member in list_obj.board.members]:
            card_ns.abort(403, 'Access denied')
        data = request.json
        title = data.get('title')
        description = data.get('description', '')
        position = data.get('position', 0)
        if not title:
            card_ns.abort(400, 'Title is required')
        new_card = Card(title=title, description=description, list_id=list_id, position=position)
        db.session.add(new_card)
        db.session.commit()
        return new_card, 201

@card_ns.route('/<int:card_id>/move')
class CardMove(Resource):
    @jwt_required()
    @card_ns.expect(card_move_model)
    def patch(self, card_id):
        card = Card.query.get_or_404(card_id)
        user_id = get_jwt_identity()
        if user_id not in [member.id for member in card.list.board.members]:
            card_ns.abort(403, 'Access denied')
        data = request.json
        target_list_id = data.get('list_id')
        target_position = data.get('position')
        if target_list_id is None or target_position is None:
            card_ns.abort(400, 'list_id and position are required')
        target_list = List.query.get_or_404(target_list_id)
        if user_id not in [member.id for member in target_list.board.members]:
            card_ns.abort(403, 'Access denied')
        # Adjust positions of cards in target list
        cards_in_target = Card.query.filter_by(list_id=target_list_id).order_by(Card.position).all()
        for c in cards_in_target:
            if c.position >= target_position:
                c.position += 1
        # Adjust positions in original list if moving between lists
        if card.list_id != target_list_id:
            cards_in_original = Card.query.filter_by(list_id=card.list_id).order_by(Card.position).all()
            for c in cards_in_original:
                if c.position > card.position:
                    c.position -= 1
        card.list_id = target_list_id
        card.position = target_position
        db.session.commit()
        return {'message': 'Card moved successfully'}, 200
