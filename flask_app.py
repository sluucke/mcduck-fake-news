from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from LLM import ChatGPT, IBGEParser, Parser
import json

app = Flask(__name__,
            static_url_path='/public',
            static_folder='public'
            )
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///minhabase.sqlite3"
db = SQLAlchemy(app)
UPLOAD_FOLDER = '/home/duckdavid/mysite/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '6537b410-df31-4078-aa58-78f6d90bdf8c'


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    searchs = db.relationship('Searchs', backref='users')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Searchs(db.Model):
    __tablename__ = "searchs"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question = db.Column(db.String)
    answer = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


def verify(username, password):
    user = Users.query.filter_by(username=username).first()
    if (user and user.password == password):
        return True

    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    is_logged = False
    searchs = []
    if 'username' in session:
        is_logged = True
        user = Users.query.filter_by(username=session['username']).first()
        print(user.id)
        searchs = Searchs.query.filter(Searchs.author_id == user.id).all()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (verify(username, password) == True):
            session['username'] = request.form['username']
            return redirect('/')
        else:
            user = Users(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = request.form['username']

        return redirect('/')

    return render_template("index.html", is_logged=is_logged, prompts=searchs)


@app.route('/llm', methods=['POST'])
def llm():
    data: str = request.data

    json_data = json.loads(data)
    user_prompt = json_data['prompt']

    if user_prompt == "":
        return {'content': "Prompt is empty"}

    chat = ChatGPT()
    ibgeParser = IBGEParser()
    parser = ibgeParser.chat_prompt(user_prompt)
    # ibgeParser.generate_csv_data(user_prompt)
    # docs = ibgeParser.parse_llm(user_prompt)
    # prompt = ibgeParser.prompt_maker()
    content = chat.chat_prompt(
        prompt=parser['prompt'], data=parser['docs'], afirmacao=user_prompt)
    if 'username' in session:
        try:
            user = Users.query.filter_by(username=session['username']).first()
            new_search = Searchs(
                author_id=user.id, question=user_prompt, answer=content)
            db.session.add(new_search)
            db.session.commit()
        except:
            print("Error on save search")
            pass

    return {
        'content': content
    }


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
