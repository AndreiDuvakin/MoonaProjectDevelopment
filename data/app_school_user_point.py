import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class UserPoint(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user_point'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey("users.id"), nullable=True)
    home_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
