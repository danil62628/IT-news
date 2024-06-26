import os
from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_migrate import Migrate


app = Flask(__name__)
 # Установка параметров базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://it_news_database_user:RFTQ4IOg4AdyRnX3JLXAAfOy0SNxhBru@dpg-conr7nsf7o1s73fqccjg-a.oregon-postgres.render.com/it_news_database'
app.secret_key = os.urandom(24)  # Генерация секретного ключа
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
   

if __name__ == '__main__':
    app.run(host='0.0.0.0')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)

def __init__(self, username, password):
        self.username = username
        self.set_password(password)

def set_password(self, password):
        self.password = generate_password_hash(password)

def check_password(self, password):
        return check_password_hash(self.password, password)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    comments = relationship("Comment", back_populates="article")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article = relationship("Article", back_populates="comments")

# Главная страница
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login') 
    else:
        articles = Article.query.all() 
        return render_template('index.html', articles=articles)


# Cтатьи
def get_article(article_id):
    article = db.session.query(Article).get(article_id)
    return article
@app.route("/article/<int:article_id>")
def article(article_id):
    if 'user_id' not in session:
        return redirect('/login') 
    else:
        article = get_article(article_id) 
        comments = db.session.query(Comment, User).join(User).all() 
        return render_template("article.html", article=article, comments=comments)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return redirect('/register')
        if len(username) < 4 or len(username) > 20:
            flash('Логин должен содержать от 4 до 20 символов', 'error')
            return redirect('/register')
        if len(password) < 4 or len(password) > 20:
            flash('Пароль должен содержать от 4 до 20 символов', 'error')
            return redirect('/register')
        if ' ' in username or ' ' in password:
            flash('Логин и пароль не должны содержать пробелы', 'error')
            return redirect('/register')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Такой пользователь уже зарегистрирован', 'error')
            return redirect('/register')
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Вы успешно зарегистрированы', 'success')
        return redirect('/login')
    return render_template('register.html')

# Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['user_id'] = user.id
            flash('Вы успешно вошли', 'success')

            flash_messages = list(get_flashed_messages())
            flash_messages.clear()
            app.view_functions[request.endpoint].clear_flash = True

            return redirect('/')
        else:
            flash('Неверные логин или пароль', 'error')
            return redirect('/login')   
    
    return render_template('login.html')



    #Добавление комментариев 
@app.route('/article/<int:article_id>/add_comment', methods=['POST'])
def add_comment(article_id):
       content = request.form.get('content')
       user_id = session.get('user_id') 

       if user_id is not None:  
            article = Article.query.get(article_id)
            user = User.query.get(user_id)  
      
       if content and article:
           new_comment = Comment(content=content, article_id=article_id, user_id=user_id)
           db.session.add(new_comment)
           db.session.commit()
           db.session.close()

       return redirect(url_for('article', article_id=article_id))


    #Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')