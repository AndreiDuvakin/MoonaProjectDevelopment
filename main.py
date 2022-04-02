from random import randint

from PIL import Image
from flask import Flask, render_template
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from forms.register import RegisterForm, Confirmation
from post import mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moona_secret_key'
help_arg = None


def save_photo(photo, login):
    size = (250, 250)
    im = Image.open(photo)
    im.thumbnail(size)
    im.save(f'static/img/user_photo/{login}.png')
    return f'static/img/user_photo/{login}.png'


def secret_key():
    return ''.join([str(randint(0, 9)) for i in range(5)])


@app.route('/')
def main_page():
    return render_template('base.html', title='moona')


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    global help_arg
    form = help_arg
    session = db_session.create_session()
    conf = Confirmation()
    secret_code = secret_key()
    mail(f'Ваш секретный код: {secret_code}', form.email.data, 'Moona Код')
    if conf.validate_on_submit():
        if str(conf.code_key.data).strip() == str(secret_code).strip():
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                login=form.login.data,
                age=form.age.data,
                about=form.about.data,
                photo=save_photo(form.photo.data, form.login.data)
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
        else:
            return render_template('confirmation_reg.html', title='Подтверждение', form=form,
                                   message='Коды не совпадают')
    return render_template('confirmation_reg.html', title='Подтверждение', form=conf)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global help_arg
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        help_arg = form
        return redirect('/confirmation')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/moona_data.db")
    app.run()


if __name__ == '__main__':
    main()
