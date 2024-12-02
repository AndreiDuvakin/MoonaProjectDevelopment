from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, StringField, PasswordField, SubmitField, FileField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class RecoveryForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Восстановить')


class Conf(FlaskForm):
    code_key = StringField('Код подтверждения', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class Finish(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Восстановление')
