from flask import Blueprint, jsonify, request
from app.methods.comments import get_all_comments, create_new_comment
from app.schemas.comment import CommentSchema
from app.decorators import validate_schema

comments_blueprint = Blueprint('comments', __name__)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


@comments_blueprint.route('/', methods=['GET'])
def get_comments():
    """Маршрут для получения комментариев."""
    comments = get_all_comments()
    return jsonify(comments_schema.dump(comments))


@comments_blueprint.route('/', methods=['POST'])
@validate_schema(comment_schema)
def create_comment(data):
    """Маршрут для создания комментария."""
    data = request.json
    comment = create_new_comment(**data)
    return comment_schema.dump(comment), 201
