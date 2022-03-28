from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moona_secret_key'


@app.route('/')
def index():
    return render_template('base.html')


def run_web():
    app.run()


if __name__ == '__main__':
    run_web()
