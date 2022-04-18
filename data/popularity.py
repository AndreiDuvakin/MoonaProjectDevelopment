import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Popularity(SqlAlchemyBase, UserMixin):
    __tablename__ = 'popularity'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    post = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("posts.id"), nullable=True, default=None)
    popularity = sqlalchemy.Column(sqlalchemy.Integer,
                                   nullable=True, default=None)
    edit_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=None)
