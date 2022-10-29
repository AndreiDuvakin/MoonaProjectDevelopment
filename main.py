import datetime
import os
from random import randint, choices
from waitress import serve
import logging

from flask import Flask, render_template, request, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import abort
from werkzeug.utils import redirect
from data import db_session
from data.answer_quest import Answer
from data.diary_post import DiaryPost
from data.like import Like
from data.popularity import Popularity
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
logging.basicConfig(filename='main.log')
login_manager = LoginManager()
login_manager.init_app(app)
help_arg = False
help_arg_2 = False
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
    return render_template('/main/main.html')

@app.route('/safeappschool/login')
def safe_app_school_login():
    pass


@app.route('/safeappschool/main')
def safe_app_school_main():
    pass


@app.route('/safeappschool/about')
def safe_app_school_about():
    pass


@app.route('/safeappschool/go')
def safe_app_school_go():
    pass


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
        if current_user.photo != '../../static/img/None_logo.png':
            photo = current_user.photo
            ph_f = True
        else:
            photo = None
        if form.del_photo.data:
            help_arg = photo
            ph_f = False
            photo = '../../static/img/None_logo.png'
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
            user.age = form.age.data
            user.about = form.about.data
            if not ph_f and form.photo.data:
                photo = save_photo(form.photo.data, logins)
            if help_arg:
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
                form.age.data = current_user.age
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
def profile():
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
                            os.remove(help_arg[3:])
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
                        os.remove(pos.photo[3:])
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
def logout():
    logout_user()
    return redirect("/diary/")


@app.route('/diary/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/diary/")
        return render_template('diary/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('diary/login.html', title='Авторизация', form=form, message='')


@app.route('/diary/confirmation', methods=['GET', 'POST'])
def confirmation():
    global help_arg
    if help_arg:
        global send_msg
        global secret_code
        global photo
        global help_arg_2
        session = db_session.create_session()
        if not help_arg_2:
            form = help_arg
            if not send_msg:
                secret_code = secret_key()
                mail(f'Ваш секретный код: {secret_code}', form.email.data, 'Moona Код')
                send_msg = True
            conf = Confirmation()
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
                            photo='../../static/img/None_logo.png'
                        )
                    user.set_password(form.password.data)
                    session.add(user)
                    session.commit()
                    send_msg = False
                    help_arg = False
                    if form.simple:
                        return redirect('/diary/simple/can_close')
                    else:
                        return redirect('/diary/login')
                else:
                    if form.simple:
                        return render_template('simple_confimication.html', title='Подтверждение', form=conf,
                                               message='Коды не совпадают')
                    else:
                        return render_template('diary/confirmation_reg.html', title='Подтверждение', form=conf,
                                               message='Коды не совпадают')
            if form.simple:
                return render_template('simple_confimication.html', title='Подтверждение', form=conf,
                                       message='Коды не совпадают')
            else:
                return render_template('diary/confirmation_reg.html', title='Подтверждение', form=conf, message='')
        else:
            conf = Confirmation()
            if not send_msg:
                secret_code = secret_key()
                mail(f'Ваш секретный код: {secret_code}', help_arg_2, 'Moona Код')
                send_msg = True
            if conf.validate_on_submit():
                if str(conf.code_key.data).strip() == str(secret_code).strip():
                    user = session.query(User).filter(User.id == current_user.id).first()
                    user.email = help_arg_2
                    help_arg_2 = 'EditEmail'
                    session.commit()
                    send_msg = False
                    help_arg = False
                    return redirect('/diary/profile')

            if form.simple:
                return render_template('simple_confimication.html', title='Подтверждение', form=conf,
                                       message='Коды не совпадают')
            else:
                return render_template('diary/confirmation_reg.html', title='Подтверждение', form=conf, message='')
    else:
        return redirect('/diary/')


@app.route('/diary/register', methods=['GET', 'POST'])
def register():
    global help_arg
    global photo
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('diary/register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('diary/register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('diary/register.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже есть")
        help_arg = form
        if form.photo.data:
            photo = save_photo(form.photo.data, form.login.data)
        return redirect('/diary/confirmation')
    return render_template('diary/register.html', title='Регистрация', form=form, message='')


@app.route('/diary/about_us')
def about():
    return render_template('diary/about.html', title='О нас')


@app.route('/diary/recovery', methods=['GET', 'POST'])
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
            mail(f'Ваш секретный код: {secret_code}', form.email.data, 'Восстановление пароля')
            send_msg = True
            return render_template('diary/recovery.html', title='Восстановление пароля', form=conf, message='', s='2')
    if conf.validate_on_submit():
        if str(conf.code_key.data).strip() == str(secret_code).strip():
            help_arg = True
            return render_template('diary/recovery.html', title='Восстановление пароля', form=finish, message='', s='3')
    if help_arg:
        if finish.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == user_email).first()
            user.set_password(finish.password.data)
            user2 = session.merge(user)
            session.add(user2)
            session.commit()
            send_msg = False
            return redirect('/diary/login')
    return render_template('diary/recovery.html', title='Восстановление пароля', form=form, message='', s='1')


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
