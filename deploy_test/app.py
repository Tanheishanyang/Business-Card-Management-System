import os
import sqlite3
from flask import Flask, render_template, g
from flask import request, redirect, url_for, flash

app = Flask(__name__)

# 设置 secret_key
app.secret_key = os.urandom(24)

# 数据库文件路径
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

# 初始化数据库
def init_db():
    with app.app_context():
        db = get_db()
        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            db.executescript(f.read())
        db.commit()

# 获取数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)  # 连接数据库
        g.db.row_factory = sqlite3.Row  # 让查询结果以字典形式返回
    return g.db

# 关闭数据库连接
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 路由：欢迎页面
@app.route('/')
def welcome():
    return render_template("Welcome/Welcome.html")

# 路由：登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        # 查询数据库，验证手机号和密码
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE phone = ? AND password = ?',
            (phone, password)
        ).fetchone()

        if user:
            flash(f"Welcome, {user['username']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid phone number or password!', 'error')
            return redirect(url_for('login'))

    return render_template("Login/Login.html")


@app.route('/logout')
def logout():
    # 在这里清除用户的会话数据
    flash('You have been logged out.', 'success')
    return redirect(url_for('welcome'))

# 路由：注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 验证两次密码是否一致
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # 验证手机号是否唯一
        db = get_db()
        existing_user = db.execute(
            'SELECT id FROM users WHERE phone = ?',
            (phone,)
        ).fetchone()
        if existing_user:
            flash('This phone has registered', 'error')  # 修改提示信息
            return redirect(url_for('register'))

        # 插入数据到数据库
        db.execute(
            'INSERT INTO users (username, phone, password) VALUES (?, ?, ?)',
            (username, phone, password)
        )
        db.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template("Register/Register.html")

# 路由：主页
@app.route('/home')
def home():
    return render_template("Home/Home.html")

if __name__ == '__main__':
    app.run(host='::', port=80, debug=True)
