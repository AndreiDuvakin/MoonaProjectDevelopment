import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Like(SqlAlchemyBase, UserMixin):
    __tablename__ = 'like'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("users.id"), nullable=True, default=None)
    post = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("posts.id"), nullable=True, default=None)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=None)
