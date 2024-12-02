from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import EmailField, StringField, PasswordField, SubmitField, FileField, DateField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    birthday = DateField('Дата рождения', validators=[DataRequired()])
    about = TextAreaField('Расскажите о себе', default='')
    photo = FileField('Фото', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')
    del_photo = SubmitField('Удалить фотографию')
    submit2 = SubmitField('Сохранить')
    simple = False
    back = False


class Confirmation(FlaskForm):
    code_key = StringField('Код подтверждения', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
