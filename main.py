from random import randint

from flask import Flask, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import redirect

from data import db_session
from data.diary_post import DiaryPost
from data.users import User
from forms.login import LoginForm
from forms.register import RegisterForm, Confirmation
from post import mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moona_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
help_arg = None
send_msg = False
secret_code = None
photo = None


def save_photo(photo, login):
    with open(f'static/img/user_photo/{login}_logo.png', 'wb') as f:
        photo.save(f)
    return f'static/img/user_photo/{login}_logo.png'


def secret_key():
    return ''.join([str(randint(0, 9)) for i in range(5)])


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('base.html', title='moona')


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    db_sess = db_session.create_session()
    posts = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id).all()
    return render_template('diary.html', title='moona', item=posts)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form, message='')


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    global help_arg
    global send_msg
    global secret_code
    global photo
    form = help_arg
    session = db_session.create_session()
    conf = Confirmation()
    if not send_msg:
        secret_code = secret_key()
        mail(f'Ваш секретный код: {secret_code}', form.email.data, 'Moona Код')
        send_msg = True
    if conf.validate_on_submit():
        if str(conf.code_key.data).strip() == str(secret_code).strip():
            if form.photo.data:
                user = User(
                    name=form.name.data,
                    surname=form.surname.data,
                    login=form.login.data,
                    age=form.age.data,
                    about=form.about.data,
                    email=form.email.data,
                    photo=photo,
                    role='user'
                )
            else:
                user = User(
                    name=form.name.data,
                    surname=form.surname.data,
                    login=form.login.data,
                    age=form.age.data,
                    about=form.about.data,
                    email=form.email.data,
                    role='user'
                )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            send_msg = False
            return redirect('/login')
        else:
            return render_template('confirmation_reg.html', title='Подтверждение', form=conf,
                                   message='Коды не совпадают')
    return render_template('confirmation_reg.html', title='Подтверждение', form=conf, message='')


@app.route('/register', methods=['GET', 'POST'])
def register():
    global help_arg
    global photo
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
        if form.photo.data:
            photo = save_photo(form.photo.data, form.login.data)
        return redirect('/confirmation')
    return render_template('register.html', title='Регистрация', form=form, message='')


def main():
    db_session.global_init("db/moona_data.db")
    app.run()


if __name__ == '__main__':
    main()
