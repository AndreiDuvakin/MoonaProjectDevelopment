import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Quest(SqlAlchemyBase, UserMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    quest = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
