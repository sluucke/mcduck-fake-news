from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
# from llm import ChatGPT, IBGEParser
import llm
import datetime
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
    
    def handleDeleteSearch(search_id):
        search = Searchs.query.filter_by(id=search_id).first()
        db.session.delete(search)
        db.session.commit()
        return redirect('/')
    
    # most_searchs = Searchs.query.order_by(Searchs.created_at.desc()).limit(5).all()



    return render_template("index.html", is_logged=is_logged, prompts=searchs, handleDeleteSearch=handleDeleteSearch)


@app.route('/llm', methods=['POST'])
def llmroute():
    data: str = request.data

    json_data = json.loads(data)
    user_prompt = json_data['prompt']
    search_id = json_data['search_id'] if 'search_id' in json_data else None

    if user_prompt == "":
        return {'content': "Prompt is empty"}
    

    # searchs = Searchs.query.filter(Searchs.question.like(f'%{user_prompt}%')).all()

    start_of_month = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    searchs = Searchs.query.filter(Searchs.created_at >= start_of_month).all()


    searchs = [search.question for search in searchs]
    print(searchs, 'searchs')

    proxy = llm.Proxy().check_similar_query(user_prompt, searchs)
    
    if(int(proxy) > 0):
        search = Searchs.query.filter_by(id=int(proxy)).first()
        return {
            'id': search.id,
            'query': search.question,
            'content': search.answer
        }
    
    chat = llm.ChatGPT()
    ibgeParser = llm.IBGEParser()
    parser = ibgeParser.chat_prompt(user_prompt)
    # ibgeParser.generate_csv_data(user_prompt)
    # docs = ibgeParser.parse_llm(user_prompt)
    # prompt = ibgeParser.prompt_maker()
    content = chat.chat_prompt(
        prompt=parser['prompt'], data=parser['docs'], afirmacao=user_prompt)
    new_search = None
    if ('username' in session):
        try:
            if search_id:
                new_search = Searchs.query.filter_by(id=int(search_id)).first()
                new_search.question = user_prompt
                new_search.answer = content
                new_search.created_at = datetime.datetime.now()
                db.session.commit()
            else:
                user = Users.query.filter_by(username=session['username']).first()
                new_search = Searchs(
                    author_id=user.id, question=user_prompt, answer=content)
                db.session.add(new_search)
                db.session.commit()
        except:
            print("Error on save search")
            pass

    return {
        'id': new_search.id if new_search else None,
        'query': user_prompt,
        'content': content
    }


@app.route('/search/<id>', methods=['GET', 'POST', 'DELETE'])
def search(id):
    if request.method == 'DELETE':
        search = Searchs.query.filter_by(id=id).first()
        db.session.delete(search)
        db.session.commit()
        return {
            'success': True
        }

    if request.method == 'POST':
        search = Searchs.query.filter_by(id=id).first()
        search.question = request.form['query']
        search.answer = request.form['answer']
        search.created_at = datetime.datetime.now()
        db.session.commit()
        return {
            'id': search.id,
            'query': search.question,
            'content': search.answer
        }

    search = Searchs.query.filter_by(id=id).first()
    return {
        'id': search.id,
        'query': search.question,
        'content': search.answer
    }


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
