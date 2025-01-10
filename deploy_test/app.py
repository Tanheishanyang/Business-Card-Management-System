# main.py

import os
import sqlite3
import base64

from flask import Flask, render_template, g
from flask import request, redirect, url_for, flash, jsonify
from flask import session

app = Flask(__name__)
# 设置 secret_key（用于 session、flash 等）
app.secret_key = os.urandom(24)

# 数据库文件路径（假设 database.db 与 main.py 同目录）
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')


# --------------- 数据库初始化 ---------------
def init_db():
    """初始化数据库：执行 schema.sql 脚本，创建表结构"""
    with app.app_context():
        db = get_db()
        # 读取 schema.sql 里的语句
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()


def get_db():
    """获取数据库连接（每个请求只连接一次）"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # 查询结果以字典形式返回
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束后自动关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# --------------- 查询 info 表的人员信息 ---------------
def get_info_list():
    """查询 info 表中的所有人员信息，并将图片 BLOB 转为 base64"""
    db = get_db()
    # 假设 info 表的字段：id, name, phone, title, address, image
    rows = db.execute('SELECT id, name, phone, title, address, image FROM info').fetchall()

    info_list = []
    for row in rows:
        image_blob = row['image']  # BLOB 字段
        if image_blob:
            # 转 base64
            image_base64 = base64.b64encode(image_blob).decode('utf-8')
            # 拼接成可直接用于 <img src="...">
            image_src = f"data:image/jpeg;base64,{image_base64}"
        else:
            # 如果数据库里没有图片，可用默认图片
            image_src = "/static/images/default_user.png"

        info_list.append({
            "id": row['id'],
            "name": row['name'],
            "phone": row['phone'],
            "title": row['title'],
            "address": row['address'],
            "image": image_src
        })

    return info_list


# --------------- 路由 ---------------
# 欢迎页
@app.route('/')
def welcome():
    return render_template("Welcome/Welcome.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE phone = ? AND password = ?',
            (phone, password)
        ).fetchone()

        if user:
            # 将用户信息存到 session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['phone'] = user['phone']
            # 你也可以在这里存更多信息，比如 session['title'] = user['title']

            flash(f"Welcome, {user['username']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid phone number or password!', 'error')
            return redirect(url_for('login'))

    return render_template("Login/Login.html")


# 登录成功欢迎界面
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('请先登录！', 'error')
        return redirect(url_for('login'))

    employees = get_info_list()

    # 从 session 获取当前登录用户信息
    # 如果没有登录，就给个默认值
    current_username = session.get('username', '未登录')
    current_phone = session.get('phone', '暂无')

    return render_template(
        "Home/Home.html",
        employees=employees,
        username=current_username,
        phone=current_phone
    )


# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出。', 'success')
    return redirect(url_for('welcome'))


# 注册
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

        # 验证手机号是否已被注册
        db = get_db()
        existing_user = db.execute(
            'SELECT id FROM users WHERE phone = ?',
            (phone,)
        ).fetchone()
        if existing_user:
            flash('This phone has already been registered.', 'error')
            return redirect(url_for('register'))

        # 插入新用户
        db.execute(
            'INSERT INTO users (username, phone, password) VALUES (?, ?, ?)',
            (username, phone, password)
        )
        db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template("Register/Register.html")


# --------------- 新增路由：添加员工信息 ---------------
@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "未登录"}), 401

    name = request.form.get('name')
    phone = request.form.get('phone')
    title = request.form.get('title')
    address = request.form.get('address')
    image = request.files.get('image')

    # 基本验证
    if not all([name, phone, title, address]):
        return jsonify({"status": "error", "message": "所有字段都是必填的"}), 400

    # 处理图片
    image_data = None
    if image:
        # 验证文件类型（这里只允许JPEG和PNG格式）
        if image.mimetype not in ['image/jpeg', 'image/png']:
            return jsonify({"status": "error", "message": "只允许上传JPEG或PNG格式的图片"}), 400
        # 你可以添加更多的验证，比如文件大小
        image_data = image.read()

    # 插入到数据库
    db = get_db()
    try:
        db.execute(
            'INSERT INTO info (name, phone, title, address, image) VALUES (?, ?, ?, ?, ?)',
            (name, phone, title, address, image_data)
        )
        db.commit()
        return jsonify({"status": "success", "message": "添加成功"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": "数据库错误"}), 500


# --------------- 主入口 ---------------
if __name__ == '__main__':
    # 检查数据库是否存在，若不存在则初始化
    if not os.path.exists(DATABASE):
        init_db()
        print("数据库已初始化。")
    app.run(host='0.0.0.0', port=80, debug=True)
