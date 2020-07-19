from app import db
from app import login
import os
from app import app

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    files = db.relationship('File', backref = 'author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def uploaded_files(self):
        return File.query.filter(User.id == File.user_id).order_by(File.timestamp.desc())



class File(db.Model):
    id = db.Column(db.String(36), primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(100), unique = True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    expire_time = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), index=True)

    def __repr__(self):
        return '<File {}>'.format(self.path)

    def size(self):
        return str(os.stat(self.path).st_size)

    def is_expired(self):
        if self.expire_time > datetime.utcnow():
            print('False')
            return False
        else:
            db.session.delete(self)
            db.session.commit()
            path = os.path.join(app.instance_path, 'files', self.id)
            os.remove(path)
            print("True")
            return True
            

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
