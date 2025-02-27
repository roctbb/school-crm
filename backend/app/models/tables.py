from app.infrastructure import db

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
