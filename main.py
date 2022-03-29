from flask import Flask, render_template

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moona_secret_key'


@app.route('/')
def main_page():
    return render_template('base.html', title='moona')


def main():
    db_session.global_init("db/moona_data.db")
    app.run()


if __name__ == '__main__':
    main()
