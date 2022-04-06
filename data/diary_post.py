import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class DiaryPost(SqlAlchemyBase, UserMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"), nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.Text)
    public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    pos_emot = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    nig_emot = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
