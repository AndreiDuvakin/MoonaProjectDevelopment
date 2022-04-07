from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddQuest(FlaskForm):
    quest = StringField('Введите новый вопрос', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
