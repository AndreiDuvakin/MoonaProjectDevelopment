from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField


class PointForm(FlaskForm):
    home_address = TextAreaField('Адрес дома:')
    school_address = TextAreaField('Адрес школы:')
    submit = SubmitField('Сохранить')
