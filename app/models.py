from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    files = db.relationship('File', backred = 'author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path = db.Column(db.String(None), unique = True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    expire_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<File {}>'.format(self.path)
