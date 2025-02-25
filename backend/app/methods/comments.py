from app.models.comment import Comment
from app.database import db


def get_all_comments():
    """Получить все комментарии."""
    return Comment.query.all()


def create_new_comment(data):
    """Создать новый комментарий."""
    comment = Comment(**data)
    db.session.add(comment)
    db.session.commit()
    return comment
