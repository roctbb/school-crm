from .tables import *
from datetime import datetime
import time
import uuid


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(100), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())

    objects = db.relationship('Object', secondary=users_objects, back_populates='owners')
    identity_object = db.relationship(
        'Object', secondary=user_identity_objects, back_populates='identity_user',
        uselist=False, lazy='select'
    )
    telegram_connection = db.relationship(
        'TelegramConnection', cascade='all, delete-orphan', back_populates='user', uselist=False
    )
    telegram_link_tokens = db.relationship(
        'TelegramLinkToken', cascade='all, delete-orphan', back_populates='user'
    )
    notifications = db.relationship(
        'Notification', cascade='all, delete-orphan', back_populates='user'
    )
    auth_refresh_tokens = db.relationship(
        'AuthRefreshToken', cascade='all, delete-orphan', back_populates='user'
    )

    def get_user_id(self):
        return str(self.id)


class AuthRefreshToken(db.Model):
    __tablename__ = 'auth_refresh_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    family_id = db.Column(db.String(36), nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    replaced_by_jti = db.Column(db.String(36), nullable=True)

    user = db.relationship('User', back_populates='auth_refresh_tokens')


class OAuthClient(db.Model):
    __tablename__ = 'oauth_clients'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(120), nullable=False, unique=True)
    client_secret_hash = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    redirect_uris = db.Column(db.JSON, nullable=False, server_default=db.text("'[]'::json"))
    post_logout_redirect_uris = db.Column(
        db.JSON, nullable=False, server_default=db.text("'[]'::json")
    )
    allowed_scopes = db.Column(
        db.JSON, nullable=False,
        server_default=db.text("'[\"openid\", \"profile\", \"email\", \"roles\"]'::json"),
    )
    allowed_roles = db.Column(
        db.JSON, nullable=False,
        server_default=db.text("'[\"student\", \"teacher\", \"admin\"]'::json"),
    )
    is_confidential = db.Column(db.Boolean, nullable=False, server_default=db.true())
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.true())
    can_send_notifications = db.Column(db.Boolean, nullable=False, server_default=db.false())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    creator = db.relationship('User', foreign_keys=[creator_id], lazy='joined')
    authorization_codes = db.relationship(
        'OAuthAuthorizationCode', cascade='all, delete-orphan', back_populates='client'
    )
    tokens = db.relationship('OAuthToken', cascade='all, delete-orphan', back_populates='client')
    consents = db.relationship('OAuthConsent', cascade='all, delete-orphan', back_populates='client')

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return (self.redirect_uris or [None])[0]

    def get_allowed_scope(self, scope):
        requested = (scope or '').split()
        allowed = set(self.allowed_scopes or [])
        return ' '.join(item for item in requested if item in allowed)

    def check_redirect_uri(self, redirect_uri):
        return redirect_uri in (self.redirect_uris or [])

    def check_client_secret(self, client_secret):
        if not self.is_confidential or not self.client_secret_hash or not client_secret:
            return False
        from application.infrastructure import bcrypt
        return bcrypt.check_password_hash(self.client_secret_hash, client_secret)

    def check_endpoint_auth_method(self, method, endpoint):
        if self.is_confidential:
            return method in {'client_secret_basic', 'client_secret_post'}
        return method == 'none'

    def check_response_type(self, response_type):
        return response_type == 'code'

    def check_grant_type(self, grant_type):
        return grant_type in {'authorization_code', 'refresh_token'}


class TelegramConnection(db.Model):
    __tablename__ = 'telegram_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True
    )
    chat_id = db.Column(db.BigInteger, nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(255), nullable=True)
    linked_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user = db.relationship('User', back_populates='telegram_connection')


class TelegramLinkToken(db.Model):
    __tablename__ = 'telegram_link_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='telegram_link_tokens')


class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = (
        db.UniqueConstraint(
            'source_client_id', 'idempotency_key', name='uq_notifications_client_idempotency'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    source_client_id = db.Column(
        db.String(120), db.ForeignKey('oauth_clients.client_id', ondelete='SET NULL'), nullable=True
    )
    source_name = db.Column(db.String(120), nullable=False)
    idempotency_key = db.Column(db.String(128), nullable=True)
    payload_hash = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    email_sent_at = db.Column(db.DateTime, nullable=True)
    telegram_sent_at = db.Column(db.DateTime, nullable=True)
    email_error = db.Column(db.Text, nullable=True)
    telegram_error = db.Column(db.Text, nullable=True)

    user = db.relationship('User', back_populates='notifications')
    source_client = db.relationship('OAuthClient', foreign_keys=[source_client_id], lazy='joined')


class OAuthConsent(db.Model):
    __tablename__ = 'oauth_consents'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'client_id', name='uq_oauth_consents_user_client'),
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(120), db.ForeignKey('oauth_clients.client_id', ondelete='CASCADE'), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    scopes = db.Column(db.JSON, nullable=False, server_default=db.text("'[]'::json"))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    client = db.relationship('OAuthClient', back_populates='consents')
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')


class OAuthAuthorizationCode(db.Model):
    __tablename__ = 'oauth_authorization_codes'

    id = db.Column(db.Integer, primary_key=True)
    code_hash = db.Column(db.String(64), nullable=False, unique=True)
    client_id = db.Column(
        db.String(120), db.ForeignKey('oauth_clients.client_id', ondelete='CASCADE'), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    redirect_uri = db.Column(db.Text, nullable=False)
    scope = db.Column(db.Text, nullable=False)
    nonce = db.Column(db.String(255), nullable=False)
    code_challenge = db.Column(db.String(128), nullable=False)
    code_challenge_method = db.Column(db.String(10), nullable=False, server_default='S256')
    auth_time = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    client = db.relationship('OAuthClient', back_populates='authorization_codes')
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope

    def get_nonce(self):
        return self.nonce

    def get_auth_time(self):
        return self.auth_time

    def get_acr(self):
        return None

    def get_amr(self):
        return ['pwd']


class OAuthToken(db.Model):
    __tablename__ = 'oauth_tokens'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(120), db.ForeignKey('oauth_clients.client_id', ondelete='CASCADE'), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    access_token_hash = db.Column(db.String(64), nullable=False, unique=True)
    refresh_token_hash = db.Column(db.String(64), nullable=True, unique=True)
    token_type = db.Column(db.String(40), nullable=False, server_default='Bearer')
    scope = db.Column(db.Text, nullable=False)
    issued_at = db.Column(db.Integer, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False)
    refresh_expires_at = db.Column(db.Integer, nullable=True)
    access_token_revoked_at = db.Column(db.Integer, nullable=False, server_default='0')
    refresh_token_revoked_at = db.Column(db.Integer, nullable=False, server_default='0')

    client = db.relationship('OAuthClient', back_populates='tokens')
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined')

    def check_client(self, client):
        return self.client_id == client.client_id

    def get_scope(self):
        return self.scope

    def get_expires_in(self):
        return max(0, self.issued_at + self.expires_in - int(time.time()))

    def is_expired(self):
        return self.issued_at + self.expires_in <= int(time.time())

    def is_revoked(self):
        return bool(self.access_token_revoked_at)

    def is_refresh_token_active(self):
        return bool(
            self.refresh_token_hash
            and not self.refresh_token_revoked_at
            and self.refresh_expires_at
            and self.refresh_expires_at > int(time.time())
        )

    def get_user(self):
        return self.user

    def get_client(self):
        return self.client


class ObjectType(db.Model):
    __tablename__ = 'object_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False, unique=True)

    available_attributes = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    available_params = db.Column(db.JSON, server_default=db.text("'[]'::json"))

    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    form_categories = db.relationship(
        'FormCategory',
        secondary=object_types_form_categories,
        back_populates='object_types', lazy=False
    )
    revisions = db.relationship(
        'ObjectTypeRevision', back_populates='object_type', lazy='select',
        cascade='all, delete-orphan', order_by='desc(ObjectTypeRevision.created_at)'
    )


class ObjectTypeRevision(db.Model):
    __tablename__ = 'object_type_revisions'

    id = db.Column(db.Integer, primary_key=True)
    object_type_id = db.Column(
        db.Integer, db.ForeignKey('object_types.id', ondelete='CASCADE'), nullable=False
    )
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    snapshot = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    object_type = db.relationship('ObjectType', back_populates='revisions')
    editor = db.relationship('User', foreign_keys=[editor_id], lazy='joined')


class Object(db.Model):
    __tablename__ = 'objects'

    id = db.Column(db.Integer, primary_key=True)
    sso_subject = db.Column(
        db.String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(1024), nullable=False)
    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    attributes = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    backup = db.Column(db.JSON, server_default=db.text("'{}'::json"))

    is_approved = db.Column(db.Boolean, nullable=False, server_default=db.text("'true'::boolean"))
    has_unapproved_submissions = db.Column(db.Boolean, nullable=False, server_default=db.text("'false'::boolean"))

    # foreign keys
    type_id = db.Column(db.Integer, db.ForeignKey('object_types.id', ondelete='CASCADE'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # relations
    parents = db.relationship(
        'Object',
        secondary='objects_children',
        primaryjoin=id == objects_children.c.child_id,
        secondaryjoin=id == objects_children.c.parent_id,
        backref=db.backref('children', lazy='select'),
        lazy='select'
    )

    type = db.relationship('ObjectType', lazy='joined')
    owners = db.relationship('User', secondary=users_objects, back_populates='objects', lazy='select')
    identity_user = db.relationship(
        'User', secondary=user_identity_objects, back_populates='identity_object',
        uselist=False, lazy='select'
    )

    # Исправленное отношение с Submission
    submissions = db.relationship('Submission', back_populates='object', lazy='dynamic')
    comments = db.relationship('Comment', backref='object', lazy='select')

    created_by = db.relationship('User', foreign_keys=[creator_id], lazy='joined')
    deleted_by = db.relationship('User', foreign_keys=[deleter_id], lazy='joined')
    approver_by = db.relationship('User', foreign_keys=[approver_id], lazy='joined')

    invitations = db.relationship('Invitation', backref='object', lazy=False)


class FormCategory(db.Model):
    __tablename__ = 'form_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=True)
    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    common_fields = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    forms = db.relationship('Form', backref='category')

    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'), nullable=True)

    # relations
    created_by = db.relationship('User', foreign_keys=[creator_id], lazy=False)
    deleted_by = db.relationship('User', foreign_keys=[deleter_id], lazy=False)

    object_types = db.relationship(
        'ObjectType',
        secondary=object_types_form_categories,
        back_populates='form_categories'
    )


class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_format = db.Column(db.String(32), nullable=False, server_default='default')
    available_params = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    fields = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    # keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('form_categories.id', ondelete='CASCADE'), nullable=False)

    # relations
    created_by = db.relationship('User', foreign_keys=[creator_id], lazy=False)
    deleted_by = db.relationship('User', foreign_keys=[deleter_id], lazy=False)
    submissions = db.relationship('Submission', back_populates='form', lazy='dynamic')


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    fields = db.Column(db.JSON, server_default=db.text("'[]'::json"))
    showoff_attributes = db.Column(db.JSON, server_default=db.text("'{}'::json"))
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    backup = db.Column(db.JSON, server_default=db.text("'{}'::json"))

    form_name = db.Column(db.String(100), nullable=True)
    form_category_name = db.Column(db.String(100), nullable=True)
    is_external = db.Column(db.Boolean, nullable=False, server_default=db.text("'false'::boolean"))

    is_approved = db.Column(db.Boolean, nullable=False, server_default=db.text("'true'::boolean"))

    # keys
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id', ondelete="CASCADE"), nullable=True)
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # relations
    form = db.relationship('Form', back_populates='submissions')
    object = db.relationship('Object', back_populates='submissions')  # Связывает с Object
    created_by = db.relationship('User', foreign_keys=[creator_id], lazy=False)
    deleted_by = db.relationship('User', foreign_keys=[deleter_id], lazy=False)
    approver_by = db.relationship('User', foreign_keys=[approver_id], lazy=False)


class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=True)
    key = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)

    # keys
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id', ondelete="CASCADE"), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True)

    created_by = db.relationship('User', foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])
    used_by = db.relationship('User', foreign_keys=[user_id])


class UploadedFile(db.Model):
    __tablename__ = "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=True)

    # Определяем отношение к модели User
    user = db.relationship("User", backref="uploaded_files")


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, db.ForeignKey("objects.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now(), onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    deleter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    created_by = db.relationship("User", backref="comments", lazy=False, foreign_keys=[creator_id])
    deleted_by = db.relationship('User', foreign_keys=[deleter_id])
