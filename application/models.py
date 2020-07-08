from .extensions import db, create_code, create_image, create_name
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, username, password, salt):
        self.username = username
        self.password = password
        self.salt = salt
        self.admin = False
        self.created = datetime.now()

    def __repr__(self):
        return f'<User {self.username}>'


class Monster(db.Model):
    __tablename__ = 'monster'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref(
        'monsters', lazy=True), foreign_keys=[user_id])
    monster_info_id = db.Column(db.Integer, db.ForeignKey('monster_info.id'))
    monster_info = db.relationship('MonsterInfo', backref=db.backref(
        'monsters', lazy=True), foreign_keys=[monster_info_id])

    def __init__(self, user, monster_info):
        self.user = user
        self.monster_info = monster_info

    def __repr__(self):
        return f'<Monster {self.id} {self.user_id} {self.monster_info_id}>'


class MonsterInfo(db.Model):
    __tablename__ = 'monster_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self):
        self.name = create_name()
        self.image = create_image()
        potential_code = create_code()
        while MonsterInfo.query.filter_by(code=potential_code).first():
            potential_code = create_code()
        self.code = potential_code

    def __repr__(self):
        return f'<MonsterInfo {self.name} {self.code}'
