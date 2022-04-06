import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class DiaryPost(SqlAlchemyBase, UserMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"), nullable=True, default=None)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=None)
    photo = sqlalchemy.Column(sqlalchemy.Text, default=None)
    public = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=None)
    pos_emot = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default=None)
    nig_emot = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default=None)
    link = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default=None)
