import datetime
import logging
import os
from random import randint, choices

from flask import Flask, render_template, request, jsonify, make_response, session, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from waitress import serve
from werkzeug.utils import redirect
from threading import Timer

from data import db_session
from data.app_school_user_point import UserPoint
from data.answer_quest import Answer
from data.diary_post import DiaryPost
from data.like import Like
from data.popularity import Popularity
from data.questions import Quest
from data.users import User
from forms.point_user import PointForm
from forms.add_question import AddQuest
from forms.answer_quest import AnswerQuest
from forms.login import LoginForm
from forms.post import AddPost
from forms.recovery import RecoveryForm, Conf, Finish
from forms.register import RegisterForm, Confirmation
from post import mail

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_key_for_dev')
logging.basicConfig(filename='main.log')
login_manager = LoginManager()
login_manager.init_app(app)
help_arg = False
help_arg_2 = False
send_msg = False
secret_code = None
photo = None
user_email = ""


def remove_java():
    global help_arg
    os.remove(help_arg)


def norm_data(datatime, date_or_time, r=False):
    if date_or_time == 'date':
        return '.'.join(str(datatime).split()[0].split('-')[::-1])
    elif date_or_time == 'time':
        return ':'.join(str(datatime).split()[1].split(':')[0:2])
    elif date_or_time == 'datetime':
        date = '.'.join(str(datatime).split()[0].split('-')[::-1])
        times = ':'.join(str(datatime).split()[1].split(':')[0:2])
        datatimes = date + ' ' + times if r else times + ' ' + date
        datatimes = datetime
        return datatimes


def save_photo(photo, login, post=False, id_post=None):
    if not post:
        with open(f'static/app_image/users_photo/{login}_logo.png', 'wb') as f:
            photo.save(f)
        return f'static/app_image/users_photo/{login}_logo.png'
    elif post and id_post is not None:
        with open(f'static/app_image/post_photo/{login}_post_{id_post}.png', 'wb') as f:
            photo.save(f)
        return f'static/app_image/post_photo/{login}_post_{id_post}.png'


def secret_key():
    return ''.join([str(randint(0, 9)) for i in range(5)])


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('/main/main.html', title='Добро пожаловать')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        redir = request.args.get('redir') if request.args.get('redir') else False
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                if redir:
                    return redirect(f'/{redir}')
                else:
                    return redirect('/')
            return render_template('main/login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('main/login.html', title='Авторизация', form=form, message='')
    else:
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated:
        form = RegisterForm()
        form.simple = True
        if form.validate_on_submit():
            if form.password.data != form.password2.data:
                return render_template('main/register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            data_session = db_session.create_session()
            if data_session.query(User).filter(User.login == form.login.data).first():
                return render_template('main/register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            if data_session.query(User).filter(User.email == form.email.data).first():
                return render_template('main/register.html', title='Регистрация',
                                       form=form,
                                       message="Такая почта уже есть")
            if form.photo.data:
                photo = save_photo(form.photo.data, form.login.data)
            else:
                photo = False
            session['ps'] = form.password.data
            return redirect(
                url_for('confirmation', photo=photo, name=form.name.data, surname=form.surname.data,
                        login=form.login.data,
                        birthday=form.birthday.data, about=form.about.data, email=form.email.data, form=True))
        return render_template('main/register.html', title='Регистрация', form=form, message='')
    else:
        return redirect('/')


@app.route('/user/<string:login>', methods=['GET', 'POST'])
def profile(login):
    if current_user.is_authenticated and current_user.login == login:
        message = request.args.get('message') if request.args.get('message') else ''
        form = RegisterForm()
        if form.del_photo.data:
            data_session = db_session.create_session()
            user = data_session.query(User).filter(User.id == current_user.id).first()
            os.remove(user.photo)
            user.photo = '/static/img/None_logo.png'
            data_session.commit()
            data_session.close()
            return redirect(f'/user/{login}')
        if request.method == 'GET':
            form.email.data = current_user.email
            form.name.data = current_user.name
            form.surname.data = current_user.surname
            form.birthday.data = current_user.birthday
            form.about.data = current_user.about
            form.photo.data = current_user.photo if current_user.photo and 'None' not in current_user.photo else None
        if form.submit2.data:
            data_session = db_session.create_session()
            user = data_session.query(User).filter(User.id == current_user.id).first()
            if user:
                if form.photo.data != current_user.photo:
                    if form.photo.data:
                        user.photo = save_photo(form.photo.data, login)
                user.name = form.name.data
                user.surname = form.surname.data
                user.birthday = form.birthday.data
                user.about = form.about.data
                data_session.commit()
                data_session.close()
                if form.email.data != current_user.email:
                    if data_session.query(User).filter(User.email == form.email.data).first():
                        return redirect(f'/user/{login}?message=Такая почта уже есть')
                    session['ps'] = None
                    return redirect(
                        url_for('confirmation', email_conf=True, email=form.email.data, form=True)
                    )
                return redirect(f'/user/{login}')
            else:
                abort(404)
        return render_template('main/profile.html', title='Профиль', form=form, message=message)
    elif current_user.is_authenticated and current_user.login != login:
        pass
    else:
        return redirect('/login')


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.args.get('form'):
        app_school = request.args.get('app_school') if request.args.get('app_school') else False
        email_conf = request.args.get('email_conf') if request.args.get('email_conf') else False
        data_session = db_session.create_session()
        form = RegisterForm(
            name=request.args.get('name'),
            surname=request.args.get('surname'),
            login=request.args.get('login'),
            birthday=request.args.get('birthday'),
            about=request.args.get('about'),
            email=request.args.get('email'),
            password=session['ps']
        )
        session['photo'] = request.args.get('photo')
        if 'send_msg' not in session:
            session['secret_code'] = secret_key()
            mail(f'Ваш секретный код: {session["secret_code"]}', form.email.data, 'Moona Код')
            session['send_msg'] = True
        else:
            if not session['send_msg']:
                if 'no_code' in session:
                    if not session['no_code']:
                        session['secret_code'] = secret_key()
                        mail(f'Ваш секретный код: {session["secret_code"]}', form.email.data, 'Moona Код')
                        session['send_msg'] = True
                    session['no_code'] = False
                else:
                    session['secret_code'] = secret_key()
                    mail(f'Ваш секретный код: {session["secret_code"]}', form.email.data, 'Moona Код')
                    session['send_msg'] = True
            session['send_msg'] = False
        conf = Confirmation()
        if conf.validate_on_submit():
            if str(conf.code_key.data).strip() == str(session['secret_code']).strip():
                if not email_conf:
                    if form.photo.data:
                        user = User(
                            name=form.name.data,
                            surname=form.surname.data,
                            login=form.login.data,
                            birthday=datetime.datetime.strptime(form.birthday.data, "%Y-%m-%d").date(),
                            about=form.about.data,
                            email=form.email.data,
                            photo=save_photo(session['photo'], form.login.data),
                            role='user'
                        )
                    else:
                        user = User(
                            name=form.name.data,
                            surname=form.surname.data,
                            login=form.login.data,
                            birthday=datetime.datetime.strptime(form.birthday.data, "%Y-%m-%d").date(),
                            about=form.about.data,
                            email=form.email.data,
                            role='user',
                            photo='/static/img/None_logo.png'
                        )
                    user.set_password(form.password.data)
                    data_session.add(user)
                    data_session.commit()
                    data_session.close()
                    session['send_msg'] = False
                    if app_school:
                        return redirect('/safeappschool/login')
                    else:
                        return redirect('/login')
                else:
                    user = data_session.query(User).filter(User.id == current_user.id).first()
                    if user:
                        user.email = form.email.data
                        data_session.commit()
                        data_session.close()
                        return redirect(f'/user/{current_user.login}')
                    else:
                        abort(404)
            else:
                session['no_code'] = True
                if app_school:
                    return render_template('safe_app_school/confirmation.html', title='Подтверждение', form=conf,
                                           message='Коды не совпадают')
                else:
                    return render_template('main/confirmation_reg.html', title='Подтверждение', form=conf,
                                           message='Коды не совпадают')
        else:
            if app_school:
                return render_template('safe_app_school/confirmation.html', title='Подтверждение', form=conf,
                                       message='')
            else:
                return render_template('main/confirmation_reg.html', title='Подтверждение', form=conf, message='')
    else:
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    path = request.args.get('path')
    logout_user()
    if not path:
        return redirect("/")
    else:
        return redirect(f'/{path}')


@app.route('/safeappschool')
def safe_app_school():
    return redirect('/safeappschool/main')


@app.route('/safeappschool/main', methods=['GET', 'POST'])
def safe_app_school_main():
    if current_user.is_authenticated:
        return render_template('safe_app_school/main.html', title='SafeAppSchool')
    else:
        return redirect('/safeappschool/login')


@app.route('/safeappschool/login', methods=['GET', 'POST'])
def safe_app_school_login():
    if current_user.is_authenticated:
        return redirect('/safeappschool/main')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect('/safeappschool/main')
            return render_template('/safe_app_school/login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('/safe_app_school/login.html', title='Вход', form=form, message='')


@app.route('/safeappschool/register', methods=['GET', 'POST'])
def safe_app_school_register():
    if current_user.is_authenticated:
        return redirect('/safeappschool/main')
    else:
        form = RegisterForm()
        form.simple = True
        if form.validate_on_submit():
            if form.password.data != form.password2.data:
                return render_template('simple/simple_register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            data_session = db_session.create_session()
            if data_session.query(User).filter(User.login == form.login.data).first():
                return render_template('safe_app_school/register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            if data_session.query(User).filter(User.email == form.email.data).first():
                return render_template('safe_app_school/register.html', title='Регистрация',
                                       form=form,
                                       message="Такая почта уже есть")
            if form.photo.data:
                photo = save_photo(form.photo.data, form.login.data)
            else:
                photo = False
            session['ps'] = form.password.data
            return redirect(
                url_for('confirmation', photo=photo, name=form.name.data, surname=form.surname.data,
                        login=form.login.data,
                        birthday=form.birthday.data, about=form.about.data, email=form.email.data, form=True,
                        app_school=True))
        return render_template('safe_app_school/register.html', title='Регистрация', form=form, message='')


@app.route('/safeappschool/about')
def safe_app_school_about():
    if current_user.is_authenticated:
        return render_template('safe_app_school/about.html')
    else:
        return redirect('/safe_app_school/login')


@app.route('/safeappschool/setting', methods=['GET', 'POST'])
def safe_app_school_setting():
    if current_user.is_authenticated:
        form = PointForm()
        data_session = db_session.create_session()
        point = data_session.query(UserPoint).filter(UserPoint.user == current_user.id).first()
        if form.validate_on_submit():
            if point:
                point.school_address = form.school_address.data
                point.home_address = form.home_address.data
            else:
                point = UserPoint(
                    user=current_user.id,
                    home_address=form.home_address.data,
                    school_address=form.school_address.data
                )
                data_session.add(point)
            data_session.commit()
            data_session.close()
            return redirect('/safeappschool/main')
        if point:
            form.school_address.data = point.school_address
            form.home_address.data = point.home_address
        return render_template('safe_app_school/setting.html', form=form, message='')
    else:
        return redirect('/safe_app_school/login')


@app.route('/safeappschool/go/<string:point>')
def safe_app_school_go(point):
    global help_arg
    if current_user.is_authenticated:
        data_session = db_session.create_session()
        address = data_session.query(UserPoint).filter(UserPoint.user == current_user.id).first()
        if address:
            if address.school_address and address.home_address:
                with open('static/js/safe_app_school/mapbasics_templates.js', 'r', encoding='utf-8') as file:
                    new_file = file.read().split('<point1>')
                    new_file = new_file[
                                   0] + f'\'{str(address.home_address).strip() if point == "school" else str(address.school_address).strip()}\'' \
                               + new_file[1]
                    new_file = new_file.split('<point2>')
                    new_file = new_file[
                                   0] + f'\'{str(address.school_address).strip() if point == "school" else str(address.home_address).strip()}\'' + \
                               new_file[1]
                    with open(f'static/js/safe_app_school/{str(current_user.id)}mapbasics.js', 'w',
                              encoding='utf-8') as new_js:
                        new_js.write(new_file)
                help_arg = f'static/js/safe_app_school/{str(current_user.id)}mapbasics.js'
                t = Timer(15, remove_java, args=None, kwargs=None)
                t.start()
                if point == 'home':
                    return render_template('safe_app_school/route.html', title='Маршрут домой', route='домой',
                                           path=help_arg)
                elif point == 'school':
                    return render_template('safe_app_school/route.html', title='Маршрут в школу', route='в школу',
                                           path=help_arg)
                else:
                    return redirect('/safe_app_school/main')
            else:
                return render_template('safe_app_school/route.html', title='Маршрут не указан', route=False)
        else:
            return render_template('safe_app_school/route.html', title='Маршрут не указан', route=False)
    else:
        return redirect('/safe_app_school/login')


@app.route('/diary/')
def main_diary_page():
    return render_template('diary/main.html', title='moona')


@app.route('/diary/edit_profile/<string:logins>', methods=['GET', 'POST'])
def edit_profile(logins):
    if current_user.is_authenticated:
        global photo
        global help_arg
        global help_arg_2
        form = RegisterForm()
        session = db_session.create_session()
        ph_f = False
        if 'None_logo' not in current_user.photo:
            photo = current_user.photo
            ph_f = True
        else:
            photo = None
        if form.del_photo.data:
            help_arg = photo
            ph_f = False
        if form.submit2.data:
            user = session.query(User).filter(User.login == logins).first()
            if user.email != form.email.data:
                if session.query(User).filter(User.email == form.email.data).first():
                    if not form.photo.data and help_arg:
                        help_arg = False
                    return render_template('diary/edit_profile.html', title='Редактирование профиля', form=form,
                                           ph_f=ph_f,
                                           message="Такая почта уже есть")
                else:
                    help_arg = True
                    help_arg_2 = form.email.data
                    return redirect('/diary/confirmation')
            user.name = form.name.data
            user.surname = form.surname.data
            user.birthday = form.birthday.data
            user.about = form.about.data
            photo = '../../static/img/None_logo.png'
            if not ph_f and form.photo.data:
                photo = save_photo(form.photo.data, logins)
            if help_arg == photo:
                os.remove(help_arg)
                help_arg = False
                photo = '../../static/img/None_logo.png'
            user.photo = photo
            session.commit()
            if user.email == form.email.data:
                return redirect('/diary/profile')
            else:
                help_arg_2 = form.email.data
                help_arg = False
                return redirect('/diary/confirmation')
        if request.method == "GET":
            if current_user.login == logins:
                form.email.data = current_user.email
                form.name.data = current_user.name
                form.surname.data = current_user.surname
                form.login.data = logins
                form.birthday.data = current_user.birthday
                form.about.data = current_user.about
                form.password.data = None
                form.password2.data = None
        if not form.photo.data and help_arg:
            help_arg = False
        return render_template('diary/edit_profile.html', title='Редактирование профиля', form=form, message='',
                               ph_f=ph_f)
    else:
        return redirect('/diary/login')


@app.route('/diary/profile')
def diary_profile():
    if current_user.is_authenticated:
        global help_arg_2
        db_sess = db_session.create_session()
        pub_post = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id, DiaryPost.public == 1).all()
        pub_post = pub_post[::-1]
        emotion_pub = []
        for i in pub_post:
            emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': [], 'like': None, 'is_like': 0,
                       'author': current_user}
            if i.pos_emot:
                emotion['pos_emot'] = i.pos_emot.split()
            else:
                emotion['pos_emot'] = None
            if i.nig_emot:
                emotion['nig_emot'] = i.nig_emot.split()
            else:
                emotion['nig_emot'] = None
            if i.link:
                emotion['link'] = i.link.split()
            else:
                emotion['link'] = None
            like = db_sess.query(Like).filter(Like.post == i.id).all()
            if like:
                emotion['like'] = len(like)
            if db_sess.query(Like).filter(Like.post == i.id, Like.user == current_user.id).first():
                emotion['is_like'] = 1
            emotion_pub.append(emotion)
        message = 'Ваша почта успешно изменена!' if help_arg_2 == 'EditEmail' else ''
        if help_arg_2:
            help_arg_2 = False
        return render_template('diary/profile.html', title='Профиль', pub_post=pub_post, emotion_pub=emotion_pub,
                               message=message)
    else:
        return redirect('/diary/login')


@app.route('/diary/new_like/<int:user_id>/<int:post_id>/<string:ret_href>')
def new_like(user_id, post_id, ret_href):
    if current_user.is_authenticated:
        session = db_session.create_session()
        find = session.query(Like).filter(Like.post == post_id, Like.user == user_id).first()
        if find:
            if (find.date - datetime.datetime.now()).days <= 30:
                pop = session.query(Popularity).filter(Popularity.post == post_id).first()
                pop.popularity = 10 * sum(1 if (i.date - datetime.datetime.now()).days <= 30 else 0 for i in
                                          session.query(Like).filter(Like.post == post_id).all()) - 10
                if not pop.popularity:
                    session.delete(pop)
            session.delete(find)
            session.commit()
            if ret_href != 'main':
                return redirect(f"/diary/{ret_href}")
            else:
                return redirect('/diary/')
        else:
            popular = session.query(Popularity).filter(Popularity.post == post_id).first()
            if not popular:
                pop = Popularity()
                pop.post = post_id
                pop.popularity = 10
                pop.edit_date = datetime.datetime.now()
                session.add(pop)
            else:
                popular.popularity += 10
            like = Like()
            like.user = user_id
            like.post = post_id
            like.date = datetime.datetime.now()
            session.add(like)
            session.commit()
            if ret_href != 'main':
                return redirect(f"/diary/{ret_href}")
            else:
                return redirect('/diary/')
    else:
        return redirect('/diary/')


@app.route('/diary/publications', methods=['GET', 'POST'])
def publications():
    session = db_session.create_session()
    fresh_posts_betta = session.query(DiaryPost).filter(DiaryPost.public == 1).all()[::-1]
    day, posts = 7, 20
    fresh_posts = []
    for i in fresh_posts_betta:
        copy_pos = fresh_posts_betta[::]
        if abs((i.date - datetime.datetime.now()).days) <= day:
            fresh_posts.append(copy_pos.pop(copy_pos.index(i)))
    while len(fresh_posts) < posts < len(fresh_posts) + len(fresh_posts_betta):
        copy_pos = fresh_posts_betta[::]
        day += 1
        posts -= 5
        for i in fresh_posts_betta:
            if abs((i.date - datetime.datetime.now()).days) <= day:
                fresh_posts.append(copy_pos.pop(copy_pos.index(i)))
    emotion_fresh = []
    if fresh_posts:
        for i in fresh_posts:
            emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': [],
                       'author': session.query(User).filter(User.id == i.author).first(), 'like': None, 'is_like': 0}
            if i.pos_emot:
                emotion['pos_emot'] = i.pos_emot.split()
            else:
                emotion['pos_emot'] = None
            if i.nig_emot:
                emotion['nig_emot'] = i.nig_emot.split()
            else:
                emotion['nig_emot'] = None
            if i.link:
                emotion['link'] = i.link.split()
            else:
                emotion['link'] = None
            like = session.query(Like).filter(Like.post == i.id).all()
            if like:
                emotion['like'] = len(like)
            if current_user.is_authenticated:
                if session.query(Like).filter(Like.post == i.id, Like.user == current_user.id).first():
                    emotion['is_like'] = 1
            emotion_fresh.append(emotion)
    pop = sorted(session.query(Popularity).all(), key=lambda x: x.popularity, reverse=True)
    if pop:
        if len(pop) > 50:
            pop = pop[:50]
        pop_post = list(
            map(lambda x: session.query(DiaryPost).filter(DiaryPost.public == 1, DiaryPost.id == x.post).first(), pop))
        emotion_pop = []
        for i in pop_post:
            logging.warning(f'{datetime.datetime.now()}:{i} - i_pop_post')
            emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': [],
                       'author': session.query(User).filter(User.id == i.author).first(), 'like': None,
                       'is_like': 0}
            if i.pos_emot:
                emotion['pos_emot'] = i.pos_emot.split()
            else:
                emotion['pos_emot'] = None
            if i.nig_emot:
                emotion['nig_emot'] = i.nig_emot.split()
            else:
                emotion['nig_emot'] = None
            if i.link:
                emotion['link'] = i.link.split()
            else:
                emotion['link'] = None
            like = session.query(Like).filter(Like.post == i.id).all()
            if like:
                emotion['like'] = len(like)
            if current_user.is_authenticated:
                if session.query(Like).filter(Like.post == i.id, Like.user == current_user.id).first():
                    emotion['is_like'] = 1
            emotion_pop.append(emotion)
    else:
        pop_post = []
        emotion_pop = []
    for_you = sorted(session.query(DiaryPost).filter(DiaryPost.public == 1).all(),
                     key=lambda x: (len(x.text), 1 if x.photo else 0, -(x.date - datetime.datetime.now()).days))
    if len(for_you) > 50:
        for_you_post = choices(for_you, k=50)
    else:
        for_you_post = set(for_you)
    emotion_for_you = []
    for i in for_you_post:
        emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': [],
                   'author': session.query(User).filter(User.id == i.author).first(), 'like': None, 'is_like': 0}
        if i.pos_emot:
            emotion['pos_emot'] = i.pos_emot.split()
        else:
            emotion['pos_emot'] = None
        if i.nig_emot:
            emotion['nig_emot'] = i.nig_emot.split()
        else:
            emotion['nig_emot'] = None
        if i.link:
            emotion['link'] = i.link.split()
        else:
            emotion['link'] = None
        like = session.query(Like).filter(Like.post == i.id).all()
        if like:
            emotion['like'] = len(like)
        if current_user.is_authenticated:
            if session.query(Like).filter(Like.post == i.id, Like.user == current_user.id).first():
                emotion['is_like'] = 1
        emotion_for_you.append(emotion)
    return render_template('diary/publications.html', fresh_post=fresh_posts, emotion_fresh=emotion_fresh,
                           title='Публикации',
                           pop_post=pop_post, emotion_pop=emotion_pop, for_you_post=for_you_post,
                           emotion_for_you=emotion_for_you)


@app.route('/diary/answer_quest/<int:id>', methods=['GET', 'POST'])
def answer_quest(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        answer = AnswerQuest()
        quest = session.query(Quest).filter(Quest.id == id).first()
        if request.method == 'GET':
            if session.query(Answer).filter(Answer.id_question == id, Answer.user == current_user.id).first():
                ans_quest = session.query(Answer).filter(Answer.id_question == id,
                                                         Answer.user == current_user.id).first()
                answer.answer.data = ans_quest.answer
        if answer.validate_on_submit():
            if not session.query(Answer).filter(Answer.id_question == id, Answer.user == current_user.id).first():
                answer_user = Answer(id_question=id,
                                     answer=answer.answer.data,
                                     user=current_user.id,
                                     date=datetime.date.today())
                quest.one_used = True
                if len(session.query(Answer).filter(Answer.id_question == id).all()) == len(session.query(User).all()):
                    quest.all_used = True
                session.add(answer_user)
                session.commit()
                return redirect('/diary/diary')
            else:
                ans_quest = session.query(Answer).filter(Answer.id_question == id).first()
                ans_quest.answer = answer.answer.data
                session.commit()
                return redirect('/diary/diary')
        return render_template('diary/answer_quest.html', tetle='Ответ на вопрос', form=answer, message='', quest=quest)
    else:
        return redirect('/diary/')


@app.route('/diary/delete_quest/<int:id>', methods=['GET', 'POST'])
def delete_quest(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        pos = session.query(Quest).filter(Quest.id == id).first()
        if pos:
            session.delete(pos)
            session.commit()
        else:
            abort(404)
        return redirect('/diary/add_question')
    else:
        return redirect('/diary/')


@app.route('/diary/add_question', methods=['GET', 'POST'])
def add_question():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            que = AddQuest()
            session = db_session.create_session()
            if que.validate_on_submit():
                if que.quest.data in list(map(lambda x: x.quest, session.query(Quest).all())):
                    return render_template('diary/add_question.html', message='Такой вопрос уже есть!',
                                           title='Добавить вопрос',
                                           form=que)
                new_que = Quest()
                new_que.quest = que.quest.data.strip()
                session.add(new_que)
                session.commit()
                que.quest.data = ''
            return render_template('diary/add_question.html', message='', title='Добавить вопрос', form=que,
                                   question=session.query(Quest).all())
        else:
            return redirect('/diary/')
    else:
        return redirect('/diary/')


@app.route('/diary/post/<int:id>', methods=['GET', 'POST'])
def post_edit(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        find_post = session.query(DiaryPost).filter(DiaryPost.id == id).first()
        if find_post:
            if find_post.author == current_user.id:
                global photo
                global help_arg
                post_ed = AddPost()
                ph_f = False
                if post_ed.del_photo.data:
                    help_arg = photo
                    photo = None
                if request.method == "GET":
                    session = db_session.create_session()
                    post_exc = session.query(DiaryPost).filter(DiaryPost.id == id,
                                                               DiaryPost.author == current_user.id).first()
                    if post_exc:
                        post_ed.name.data = post_exc.name
                        post_ed.text.data = post_exc.text
                        post_ed.public.data = post_exc.public
                        post_ed.pos_emot.data = post_exc.pos_emot
                        post_ed.nig_emot.data = post_exc.nig_emot
                        post_ed.link.data = post_exc.link
                        if post_exc.photo:
                            photo = post_exc.photo
                            ph_f = True
                        else:
                            photo = None
                    else:
                        abort(404)
                if post_ed.validate_on_submit() and not post_ed.del_photo.data:
                    session = db_session.create_session()
                    post_exc = session.query(DiaryPost).filter(DiaryPost.id == id,
                                                               DiaryPost.author == current_user.id).first()
                    if post_exc:
                        post_exc.name = post_ed.name.data
                        post_exc.text = post_ed.text.data
                        post_exc.public = post_ed.public.data
                        post_exc.pos_emot = post_ed.pos_emot.data
                        post_exc.nig_emot = post_ed.nig_emot.data
                        post_exc.link = post_ed.link.data
                        if help_arg:
                            os.remove(help_arg)
                            help_arg = False
                        if post_ed.photo.data:
                            post_exc.photo = save_photo(post_ed.photo.data, current_user.login, post=True,
                                                        id_post=post_exc.id)
                        else:
                            post_exc.photo = photo
                        check_pop = session.query(Popularity).filter(Popularity.post == post_exc.id).first()
                        if not post_ed.public.data and check_pop:
                            session.delete(check_pop)
                        session.commit()
                        return redirect('/diary/diary')
                    else:
                        abort(404)
                return render_template('diary/post.html', form=post_ed, message='', title='Изменить запись', pht=ph_f)
            else:
                return redirect('/diary/diary')
        else:
            return redirect('/diary/diary')
    else:
        return redirect('/diary/login')


@app.route('/diary/post_deleted/<int:id>', methods=['GET', 'POST'])
def post_deleted(id):
    if current_user.is_authenticated:
        session = db_session.create_session()
        find_post = session.query(DiaryPost).filter(DiaryPost.id == id).first()
        if find_post:
            if find_post.author == current_user.id or current_user.role == 'admin':
                session = db_session.create_session()
                pos = session.query(DiaryPost).filter(DiaryPost.id == id).first()
                if pos:
                    if pos.photo:
                        os.remove(pos.photo)
                    likes = session.query(Like).filter(Like.post == pos.id).all()
                    if likes:
                        list(map(lambda i: session.delete(i), likes))
                    pop = session.query(Popularity).filter(Popularity.post == pos.id).first()
                    if pop:
                        session.delete(pop)
                    session.delete(pos)
                    session.commit()
                else:
                    abort(404)
                return redirect('/diary/diary')
            else:
                return redirect('/diary/diary')
        else:
            return redirect('/diary/diary')
    else:
        return redirect('/diary/login')


@app.route('/diary/add_post', methods=['GET', 'POST'])
def add_post():
    if current_user.is_authenticated:
        pos = AddPost()
        session = db_session.create_session()
        if pos.validate_on_submit():
            try:
                id = session.query(DiaryPost).order_by(DiaryPost.id)[-1].id
                if id:
                    id += 1
                else:
                    id = -1
            except Exception:
                id = -1
            if pos.photo.data:
                diart_pos = DiaryPost(name=pos.name.data,
                                      text=pos.text.data,
                                      author=current_user.id,
                                      date=datetime.datetime.now(),
                                      photo=save_photo(pos.photo.data, current_user.login, post=True, id_post=id),
                                      public=pos.public.data,
                                      pos_emot=pos.pos_emot.data,
                                      nig_emot=pos.nig_emot.data,
                                      link=pos.link.data)
                session.add(diart_pos)
                session.commit()
                return redirect("/diary/diary")
            else:
                diart_pos = DiaryPost(name=pos.name.data,
                                      text=pos.text.data,
                                      author=current_user.id,
                                      date=datetime.datetime.now(),
                                      public=pos.public.data,
                                      pos_emot=pos.pos_emot.data,
                                      nig_emot=pos.nig_emot.data,
                                      link=pos.link.data)
                session.add(diart_pos)
                session.commit()
                return redirect("/diary/diary")
        return render_template('diary/post.html', form=pos, title='Новый пост', message='')
    else:
        return redirect('/diary/login')


@app.route('/diary/diary', methods=['GET', 'POST'])
def diary():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id).all()
        posts = posts[::-1]
        pub_post = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id, DiaryPost.public == 1).all()
        pub_post = pub_post[::-1]
        emotion_pub = []
        for i in pub_post:
            emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': [], 'like': None, 'is_like': 0}
            if i.pos_emot:
                emotion['pos_emot'] = i.pos_emot.split()
            else:
                emotion['pos_emot'] = None
            if i.nig_emot:
                emotion['nig_emot'] = i.nig_emot.split()
            else:
                emotion['nig_emot'] = None
            if i.link:
                emotion['link'] = i.link.split()
            else:
                emotion['link'] = None
            like = db_sess.query(Like).filter(Like.post == i.id).all()
            if like:
                emotion['like'] = len(like)
            if db_sess.query(Like).filter(Like.post == i.id, Like.user == current_user.id).first():
                emotion['is_like'] = 1
            emotion_pub.append(emotion)
        lis_emotion = []
        for i in posts:
            emotion = {id: i.id, 'pos_emot': [], 'nig_emot': [], 'link': []}
            if i.pos_emot:
                emotion['pos_emot'] = i.pos_emot.split()
            else:
                emotion['pos_emot'] = None
            if i.nig_emot:
                emotion['nig_emot'] = i.nig_emot.split()
            else:
                emotion['nig_emot'] = None
            if i.link:
                emotion['link'] = i.link.split()
            else:
                emotion['link'] = None
            lis_emotion.append(emotion)
        quest = db_sess.query(Answer).filter(Answer.user == current_user.id).all()
        try:
            days_reg = current_user.data_reg - datetime.date.today()
            days_reg = abs(days_reg.days) + 1
            if quest:
                post_quest = db_sess.query(Quest).filter(Quest.id.in_([i.id_question for i in quest])).all()
            else:
                post_quest = []
            max_quests = len(db_sess.query(Quest).all())
            while len(post_quest) < days_reg and max_quests > len(post_quest):
                post_quest.append(
                    db_sess.query(Quest).filter(Quest.id.notin_([i.id for i in post_quest])).first())
            ans = []
            for i in post_quest:
                if i is not None:
                    ans_id = db_sess.query(Answer).filter(
                        Answer.id_question == i.id, Answer.user == current_user.id).first()
                    if ans_id is not None:
                        ans.append(ans_id)
            post_quest = post_quest[::-1]
            ans = ans[::-1]
            ans2 = {}
            for i in ans:
                ans2[i.id_question] = i
        except Exception as e:
            ans2 = []
    else:
        posts = None
        post_quest = None
        ans2 = None
        lis_emotion = None
        emotion_pub = None
        pub_post = None
    return render_template('diary/diary.html', title='Дневник', my_post=posts, message='', question=post_quest,
                           ans=ans2, emotion=lis_emotion, emotion_pub=emotion_pub, pub_post=pub_post)


@app.route('/diary/logout')
@login_required
def diary_logout():
    logout_user()
    return redirect("/diary/")


@app.route('/diary/about_us')
def about():
    return render_template('diary/about.html', title='О нас')


@app.route('/school_app_check_auth', methods=['POST'])
def check_auth():
    req = request.json
    email = req['login']
    password = req['password']
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if user:
        if user.check_password(password) or user.check_hash_password(password):
            return make_response(jsonify({
                'key': open('key.txt', 'r', encoding='utf-8').read(),
                'name': user.name,
                'surname': user.surname,
                'login': user.login,
                'hash': user.password
            }), 200)
        else:
            return abort(403)
    else:
        return abort(404)


@app.route('/simple/can_close')
def can_close():
    return render_template('simple/simple_can_close.html', title='Можете закрыть страницу')


@app.route('/simple/register', methods=['GET', 'POST'])
def school_reg():
    global help_arg
    global photo
    form = RegisterForm()
    form.simple = True
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('simple/simple_register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('simple/simple_register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('simple/simple_register.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже есть")
        help_arg = form
        if form.photo.data:
            photo = save_photo(form.photo.data, form.login.data)
        return redirect('/diary/confirmation')
    return render_template('simple/simple_register.html', title='Регистрация', form=form, message='')


def main():
    db_session.global_init("db/moona_data.db")
    try:
        serve(app, host='0.0.0.0', port=5000)
    except Exception as error:
        logging.warning(f'{datetime.datetime.now()}:{error}')
    # после запуска переходите по ссылке http://127.0.0.1:5000/ в вашем браузере


if __name__ == '__main__':
    main()
