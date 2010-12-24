from book import app
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    desc = db.Column(db.String(400))
    phones = db.relation("Phone", backref="entry", cascade="all, delete, delete-orphan")


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(60))
    desc = db.Column(db.String(400))
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))
