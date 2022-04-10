import datetime
import os
from random import randint

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from werkzeug.utils import redirect

from data import db_session
from data.answer_quest import Answer
from data.diary_post import DiaryPost
from data.questions import Quest
from data.users import User
from forms.add_question import AddQuest
from forms.answer_quest import AnswerQuest
from forms.login import LoginForm
from forms.post import AddPost
from forms.recovery import RecoveryForm, Conf, Finish
from forms.register import RegisterForm, Confirmation
from post import mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moona_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
help_arg = False
send_msg = False
secret_code = None
photo = None
user_email = ""


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
        return f'../static/app_image/users_photo/{login}_logo.png'
    elif post and id_post != None:
        with open(f'static/app_image/post_photo/{login}_post_{id_post}.png', 'wb') as f:
            photo.save(f)
        return f'../static/app_image/post_photo/{login}_post_{id_post}.png'


def secret_key():
    return ''.join([str(randint(0, 9)) for i in range(5)])


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('base.html', title='moona')


@app.route('/answer_quest/<int:id>', methods=['GET', 'POST'])
def answer_quest(id):
    session = db_session.create_session()
    answer = AnswerQuest()
    quest = session.query(Quest).filter(Quest.id == id).first()
    if request.method == 'GET':
        if session.query(Answer).filter(Answer.id_question == id).first():
            ans_quest = session.query(Answer).filter(Answer.id_question == id).first()
            answer.answer.data = ans_quest.answer
    if answer.validate_on_submit():
        if not session.query(Answer).filter(Answer.id_question == id).first():
            answer_user = Answer(id_question=id,
                                 answer=answer.answer.data,
                                 user=current_user.id,
                                 date=datetime.date.today())
            quest.one_used = True
            if len(session.query(Answer).filter(Answer.id_question == id).all()) == len(session.query(User).all()):
                quest.all_used = True
            session.add(answer_user)
            session.commit()
            return redirect('/diary')
        else:
            ans_quest = session.query(Answer).filter(Answer.id_question == id).first()
            ans_quest.answer = answer.answer.data
            session.commit()
            return redirect('/diary')
    return render_template('answer_quest.html', tetle='Ответ на вопрос', form=answer, message='', quest=quest)


@app.route('/delete_quest/<int:id>', methods=['GET', 'POST'])
def delete_quest(id):
    session = db_session.create_session()
    pos = session.query(Quest).filter(Quest.id == id).first()
    if pos:
        session.delete(pos)
        session.commit()
    else:
        abort(404)
    return redirect('/add_question')


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    que = AddQuest()
    session = db_session.create_session()
    if que.validate_on_submit():
        if que.quest.data in list(map(lambda x: x.quest, session.query(Quest).all())):
            return render_template('add_question.html', message='Такой вопрос уже есть!', title='Добавить вопрос',
                                   form=que)
        new_que = Quest()
        new_que.quest = que.quest.data.strip()
        session.add(new_que)
        session.commit()
        que.quest.data = ''
    return render_template('add_question.html', message='', title='Добавить вопрос', form=que,
                           question=session.query(Quest).all())


@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post_edit(id):
    global photo
    post_ed = AddPost()
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
            else:
                photo = None
        else:
            abort(404)
    if post_ed.validate_on_submit():
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
            if post_ed.photo.data:
                post_exc.photo = save_photo(post_ed.photo, current_user.login, post=True, id_post=post_exc.id)
            else:
                post_exc.photo = photo
            session.commit()
            return redirect('/diary')
        else:
            abort(404)
    return render_template('post.html', form=post_ed, message='', title='Изменить запись')


@app.route('/post_deleted/<int:id>', methods=['GET', 'POST'])
def post_deleted(id):
    session = db_session.create_session()
    pos = session.query(DiaryPost).filter(DiaryPost.id == id,
                                          DiaryPost.author == current_user.id).first()
    if pos:
        if pos.photo:
            os.remove(pos.photo[3:])
        session.delete(pos)
        session.commit()
    else:
        abort(404)
    return redirect('/diary')


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
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
            return redirect("/diary")
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
            return redirect("/diary")
    return render_template('post.html', form=pos, title='Новый пост', message='')


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        posts = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id).all()
        posts = posts[::-1]
        pub_post = db_sess.query(DiaryPost).filter(DiaryPost.author == current_user.id, DiaryPost.public == 1).all()
        pub_post = pub_post[::-1]
        emotion_pub = []
        for i in pub_post:
            emotion = {id: i.id,'pos_emot': [], 'nig_emot': [], 'link': []}
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
            emotion_pub.append(emotion)
        lis_emotion = []
        for i in posts:
            emotion = {id: i.id,'pos_emot': [], 'nig_emot': [], 'link': []}
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
        days_reg = current_user.data_reg - datetime.date.today()
        days_reg = abs(days_reg.days) + 1
        if quest:
            post_quest = db_sess.query(Quest).filter(Quest.id.in_([i.id_question for i in quest])).all()
        else:
            post_quest = []
        while len(post_quest) < days_reg:
            post_quest.append(
                db_sess.query(Quest).filter(Quest.id.notin_([i.id for i in post_quest])).first())
        ans = []
        for i in post_quest:
            ans_id = db_sess.query(Answer).filter(Answer.id_question == i.id and Answer.user == current_user.id).first()
            if ans_id:
                ans.append(ans_id)
        post_quest = post_quest[::-1]
        ans = ans[::-1]
        ans2 = {}
        for i in ans:
            ans2[i.id_question] = i
    else:
        posts = None
        post_quest = None
        ans2 = None
        lis_emotion = None
        emotion_pub = None
        pub_post = None
    return render_template('diary.html', title='moona', my_post=posts, message='', question=post_quest,
                           ans=ans2, emotion=lis_emotion, emotion_pub=emotion_pub, pub_post=pub_post)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.validate_on_submit())
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
        print(secret_code)
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
                    role='user',
                    photo='../static/img/Икона.png'
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


@app.route('/recovery', methods=['GET', 'POST'])
def recovery():
    global send_msg
    global secret_code
    global help_arg
    global user_email
    form = RecoveryForm()
    conf = Conf()
    finish = Finish()
    session = db_session.create_session()
    if form.validate_on_submit() and form.email.data:
        user_email = form.email.data
        if not send_msg:
            secret_code = secret_key()
            mail(f'Ваш секретный код: {secret_code}', form.email.data, 'Moona Код')
            send_msg = True
            print(secret_code)
            return render_template('recovery.html', title='Восстановление пароля', form=conf, message='', s='2')
    if conf.validate_on_submit():
        if str(conf.code_key.data).strip() == str(secret_code).strip():
            help_arg = True
            return render_template('recovery.html', title='Восстановление пароля', form=finish, message='', s='3')
    if help_arg:
        if finish.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == user_email).first()
            # user2 = User(
            #     name=user.name,
            #     surname=user.surname,
            #     login=user.login,
            #     age=user.age,
            #     about=user.about,
            #     email=user_email,
            #     photo=user.photo,
            #     role='user')
            user.set_password(finish.password.data)
            user2 = session.merge(user)
            session.add(user2)
            session.commit()
            send_msg = False
            return redirect('/login')
    return render_template('recovery.html', title='Восстановление пароля', form=form, message='', s='1')


def main():
    db_session.global_init("db/moona_data.db")
    app.run()


if __name__ == '__main__':
    main()
