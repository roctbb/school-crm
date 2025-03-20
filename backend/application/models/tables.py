from application.infrastructure import db

users_objects = db.Table(
    'users_objects',  # Убедимся, что это имя будет использоваться везде
    db.Column('object_id', db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
)

objects_children = db.Table(
    'objects_children',  # Имя таблицы
    db.Column('parent_id', db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), primary_key=True),
    db.Column('child_id', db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), primary_key=True)
)

object_user_association = db.Table(
    'object_user_association',
    db.Column('object_id', db.Integer, db.ForeignKey('objects.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

# Пример ассоциативной таблицы
object_types_form_categories = db.Table(
    'object_types_form_categories',
    db.Column('object_type_id', db.Integer, db.ForeignKey('object_types.id', ondelete='CASCADE'), primary_key=True),
    db.Column('form_category_id', db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'), primary_key=True)
)
