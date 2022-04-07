import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'answer'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    answer = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    user = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("users.id"), nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
