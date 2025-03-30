from ....core.extensions import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    user = Doctor.query.get(int(user_id))
    if user:
        return user
    user = Disinfector.query.get(int(user_id))
    if user:
        return user
    user = Administrator.query.get(int(user_id))
    return user


def get_next_user_id():
    counter = UserIDCounter.query.first()
    if counter is None:
        counter = UserIDCounter(last_id=0)
        db.session.add(counter)
        db.session.commit()

    counter.last_id += 1
    db.session.commit()
    return counter.last_id


class UserIDCounter(db.Model):
    __tablename__ = 'user_id_counter'
    id = db.Column(db.Integer, primary_key=True)
    last_id = db.Column(db.Integer, default=0)


class BaseUser(db.Model, UserMixin):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    login = db.Column(db.String(50), unique=False, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(50), nullable=False, default='disinfector')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = get_next_user_id()


class Doctor(BaseUser):
    __tablename__ = 'doctor'
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    application = db.relationship('Application', backref='doctor', lazy=True)


class Disinfector(BaseUser):
    __tablename__ = 'disinfector'
    application = db.relationship(
        'Disinfection', backref='disinfector', lazy=True)


class Administrator(BaseUser):
    __tablename__ = 'administrator'


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_area = db.Column(db.String(50), unique=True, nullable=False)
    applications = db.relationship('Doctor', backref='area', lazy=True)
    
    
