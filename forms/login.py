from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    style = {"type": "checkbox", "class": "btn-check", "id": "btn-check", "autocomplete": "off"}
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')