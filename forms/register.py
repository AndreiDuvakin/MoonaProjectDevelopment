from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, StringField, PasswordField, SubmitField, FileField, IntegerField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    about = TextAreaField('Расскажите о себе', default='')
    photo = FileField('Фото', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class Confirmation(FlaskForm):
    code_key = StringField('Код подтверждения', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
