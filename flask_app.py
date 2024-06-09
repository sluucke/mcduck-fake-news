from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__,
static_url_path='/static',
static_folder='public'
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///minhabase.sqlite3"
db = SQLAlchemy(app)
UPLOAD_FOLDER = '/home/duckdavid/mysite/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '6537b410-df31-4078-aa58-78f6d90bdf8c'

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    senha = db.Column(db.String)

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha


def verificar_crendenciais(nome, senha):
    user = Usuario.query.filter_by(nome = nome).first()
    if(user and user.senha == senha):
        return True

    return False

@app.route('/')
def index(nome):
   return render_template("index.html", visitante="David")


@app.route("/usuario", methods=[ 'POST', 'GET'])
def addUsuario():
    if (request.method == "POST"):
        nome = request.form['nome']
        senha = request.form['senha']
        user = Usuario(nome, senha)
        db.session.add(user)
        db.session.commit()
    users = Usuario.query.all()
    return render_template('usuario.html', usuarios=users)

@app.route("/formulario", methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        return render_template('formulario.html', nome=nome, senha=senha)
    else:
        return render_template('formulario.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['arquivo']
            savePath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(savePath)
            return 'upload feito com sucesso'
        return render_template('upload.html', username=session['username'])
    return 'Você não está autorizado para ver essa página. Por favor, faça login'

@app.route('/area_vip')
def area_vip():
    if 'username' in session:
        return 'Você está na área vip, logado como {}'.format(session['username'])
    return 'Você não está autorizado para ver essa página. Por favor, faça login'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome =  request.form['username']
        senha =  request.form['password']
        if(verificar_crendenciais(nome, senha) == True):
            session['username'] = request.form['username']
            return redirect(url_for('upload'))

        return 'usuário ou senha errados, tente novamente'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()

