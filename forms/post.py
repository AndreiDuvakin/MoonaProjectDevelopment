from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class AddPost(FlaskForm):
    name = StringField('Название')
    text = TextAreaField('Расскажите, что нового?')
    photo = FileField('Прикрепите фото', validators=[FileAllowed(['jpg', 'png'])])
    public = BooleanField('Опубликовать?')
    pos_emot = TextAreaField('Какие позитивные эмоции вы испытываете?')
    nig_emot = TextAreaField('Какие негативные эмоции вы испытываете?')
    link = TextAreaField('Вы можете оставить тут ссылки через пробел')
    submit = SubmitField('Сохранить')
