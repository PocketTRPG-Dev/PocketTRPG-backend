from datetime import datetime

from exts import db, JSONEncodedDict, MutableDict
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    qq = db.Column(db.String(50))

    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    invitationCode = db.Column(db.String(50))
    num_card = db.Column(db.Integer, default=0)

    user_ip_address = db.Column(db.String(50))

    def get_id(self):
        try:
            return str(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get id`')

    def get_username(self):
        try:
            return str(self.username)
        except AttributeError:
            raise NotImplementedError('No `username` attribute - override `get id`')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @property
    def is_authenticated(self):
        return True

    def is_admin(self):
        if self.role == 'Admin':
            return True
        return False

    def is_banned(self):
        if self.role == 'Banned':
            return True
        return False

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Card_Pf(db.Model):
    __tablename__ = 'card_pathfinder'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    features = db.Column(db.String(50))
    tag = db.Column(db.String(50))
    # 使用外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', backref=db.backref('card_pathfinder'))

    public = db.Column(db.Boolean, default=False)


class Card_normal(db.Model):
    __tablename__ = 'card_normal'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    features = db.Column(db.Text)
    tag = db.Column(db.String(50))
    content = db.Column(db.Text())
    create_time = db.Column(db.DateTime, default=datetime.now)
    # Json
    data = db.Column(db.JSON)
    # 使用外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', backref=db.backref('card_normal'))

    public = db.Column(db.Boolean, default=False)


class Article(db.Model):
    __tablename__ = 'article'
    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 使用外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', backref=db.backref('article'))

    tag = db.Column(db.String(20), default='Normal')
    state = db.Column(db.String(20), default='Open')
    num_comments = db.Column(db.Integer, default=0)


user_badge = db.Table('user_badge',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
                      db.Column('badge_id', db.Integer, db.ForeignKey('badge.badge_id'), primary_key=True))


class Badge(db.Model):
    __tablename__ = 'badge'
    badge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    badge_class = db.Column(db.String(20), default='label label-default')
    create_time = db.Column(db.DateTime, default=datetime.now)

    users = db.relationship('User', secondary=user_badge, backref=db.backref('badges'))


user_game = db.Table('user_game',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
                     db.Column('game_id', db.Integer, db.ForeignKey('game.game_id'), primary_key=True),
                     db.Column('name', db.String(50), default='Speaker'))


class Game(db.Model):
    __tablename__ = 'game'
    game_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)
    state = db.Column(db.String(10), default='Open')
    length = db.Column(db.Integer, default=0)
    password = db.Column(db.String(20))
    num_member = db.Column(db.Integer, default=1)
    num_group = db.Column(db.Integer, default=2)
    member_limit = db.Column(db.Integer, default=6)
    author_id = db.Column(db.Integer)
    users = db.relationship('User', secondary=user_game, backref=db.backref('games'))

    def get_author_id(self):
        try:
            return int(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `author_id` attribute')

    def validate_password(self, validation):
        try:
            if self.password == validation:
                return True
            else:
                return False
        except AttributeError:
            raise NotImplementedError('No `password` attribute')


class GamePost(db.Model):
    __tablename__ = 'game_post'
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    speaker = db.Column(db.String(20), default='Speaker')
    create_time = db.Column(db.DateTime, default=datetime.now)
    group_id = db.Column(db.Integer, default=1)
    send_to = db.Column(db.String(50))

    # 使用外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    author = db.relationship('User', backref=db.backref('game_post'))

    game_id = db.Column(db.Integer, db.ForeignKey('game.game_id'))
    game = db.relationship('Game', backref=db.backref('game_post'))


class Map(db.Model):
    __tablename__ = 'map'
    map_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    size_height = db.Column(db.Integer, default=600)
    size_weight = db.Column(db.Integer, default=800)
    # Json
    data = db.Column(db.JSON)

    # 使用外键
    game_id = db.Column(db.Integer, db.ForeignKey('game.game_id'))
    game = db.relationship('Game', backref=db.backref('map'))


class ActivationCode(db.Model):
    __tablename__ = 'activation'
    activation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(30), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    used = db.Column(db.Boolean, default=False)


class ApiToken(db.Model):
    __tablename__ = 'token'
    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(30), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)


