# main.py

import os
import sqlite3
import base64
import datetime
from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')


def init_db():
    """初始化数据库：执行 schema.sql 脚本，创建表结构"""
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()


def get_db():
    """获取数据库连接（每个请求只连接一次）"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束后自动关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def get_info_list(name_query=None, phone_query=None):
    """
    查询 info 表中的所有人员信息，或根据姓名和电话查询，并将图片 BLOB 转为 base64
    """
    db = get_db()
    query = 'SELECT id, name, phone, title, address, image FROM info WHERE 1=1'
    params = []
    if name_query:
        query += ' AND name LIKE ?'
        params.append(f'%{name_query}%')
    if phone_query:
        query += ' AND phone LIKE ?'
        params.append(f'%{phone_query}%')

    rows = db.execute(query, params).fetchall()

    info_list = []
    for row in rows:
        image_blob = row['image']
        if image_blob:
            image_base64 = base64.b64encode(image_blob).decode('utf-8')
            image_src = f"data:image/jpeg;base64,{image_base64}"
        else:
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


@app.route('/')
def welcome():
    return render_template("Welcome/Welcome.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username').strip()
        phone = request.form.get('phone').strip()
        password = request.form.get('password').strip()

        if not all([username, phone, password]):
            flash('所有字段都是必填的。', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, phone, password) VALUES (?, ?, ?)',
                (username, phone, hashed_password)
            )
            db.commit()
            flash('注册成功，请登录。', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('该电话号码已被注册。', 'error')
            return redirect(url_for('register'))
        except Exception as e:
            db.rollback()
            flash('注册时发生错误，请稍后再试。', 'error')
            return redirect(url_for('register'))

    return render_template("Register/Register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE phone = ?',
            (phone,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['phone'] = user['phone']

            flash(f"Welcome, {user['username']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid phone or password!', 'error')
            return redirect(url_for('login'))

    return render_template("Login/Login.html")


@app.route('/home')
def home():
    """主页，展示所有员工信息"""
    if 'user_id' not in session:
        flash('请先登录！', 'error')
        return redirect(url_for('login'))

    employees = get_info_list()
    current_username = session.get('username', '未登录')
    current_phone = session.get('phone', '暂无')
    return render_template("Home/Home.html", 
                           employees=employees, 
                           username=current_username, 
                           phone=current_phone)


@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('您已成功登出。', 'success')
    return redirect(url_for('welcome'))


@app.route('/add_employee', methods=['POST'])
def add_employee():
    """添加员工信息"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "未登录"}), 401

    name = request.form.get('name').strip()
    phone = request.form.get('phone').strip()
    title = request.form.get('title').strip()
    address = request.form.get('address').strip()
    image = request.files.get('image')

    if not all([name, phone, title, address]):
        return jsonify({"status": "error", "message": "所有字段都是必填的"}), 400

    image_data = None
    if image:
        if image.mimetype not in ['image/jpeg', 'image/png']:
            return jsonify({"status": "error", "message": "只允许上传JPEG或PNG格式的图片"}), 400
        image_data = image.read()

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


@app.route('/update_employee/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    """修改员工信息"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "未登录"}), 401

    name = request.form.get('name').strip()
    phone = request.form.get('phone').strip()
    title = request.form.get('title').strip()
    address = request.form.get('address').strip()
    image = request.files.get('image')

    if not all([name, phone, title, address]):
        return jsonify({"status": "error", "message": "所有字段都是必填的"}), 400

    image_data = None
    if image:
        if image.mimetype not in ['image/jpeg', 'image/png']:
            return jsonify({"status": "error", "message": "只允许上传JPEG或PNG格式的图片"}), 400
        image_data = image.read()

    db = get_db()
    try:
        if image_data:
            db.execute(
                'UPDATE info SET name = ?, phone = ?, title = ?, address = ?, image = ? WHERE id = ?',
                (name, phone, title, address, image_data, employee_id)
            )
        else:
            db.execute(
                'UPDATE info SET name = ?, phone = ?, title = ?, address = ? WHERE id = ?',
                (name, phone, title, address, employee_id)
            )
        db.commit()

        updated_employee = db.execute(
            'SELECT id, name, phone, title, address, image FROM info WHERE id = ?',
            (employee_id,)
        ).fetchone()
        if updated_employee:
            img_blob = updated_employee['image']
            if img_blob:
                img_base64 = base64.b64encode(img_blob).decode('utf-8')
                img_src = f"data:image/jpeg;base64,{img_base64}"
            else:
                img_src = "/static/images/default_user.png"

            emp_data = {
                "id": updated_employee['id'],
                "name": updated_employee['name'],
                "phone": updated_employee['phone'],
                "title": updated_employee['title'],
                "address": updated_employee['address'],
                "image": img_src
            }
            return jsonify({"status": "success", "message": "修改成功", "employee": emp_data}), 200
        else:
            return jsonify({"status": "error", "message": "未找到该员工"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": "数据库错误"}), 500


@app.route('/search_employee', methods=['GET'])
def search_employee():
    """搜索员工信息"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "未登录"}), 401

    name_query = request.args.get('name')
    phone_query = request.args.get('phone')

    employees = get_info_list(name_query, phone_query)
    return jsonify({"status": "success", "data": employees}), 200


@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    """删除员工信息：将信息移动到 deleted_info 表，并从 info 表中删除"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "未登录"}), 401

    db = get_db()

    # 查询员工信息
    row = db.execute('SELECT * FROM info WHERE id = ?', (employee_id,)).fetchone()
    if not row:
        return jsonify({"status": "error", "message": "记录不存在"}), 404

    try:
        # 插入到 deleted_info
        deleted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute('''
            INSERT INTO deleted_info (name, phone, title, address, image, deleted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['name'], row['phone'], row['title'], row['address'], row['image'], deleted_at))

        # 从 info 表删除
        db.execute('DELETE FROM info WHERE id = ?', (employee_id,))
        db.commit()

        # 准备返回给前端
        image_src = "/static/images/default_user.png"
        if row['image']:
            img_base64 = base64.b64encode(row['image']).decode('utf-8')
            image_src = f"data:image/jpeg;base64,{img_base64}"

        deleted_employee = {
            "id": row['id'],
            "name": row['name'],
            "phone": row['phone'],
            "title": row['title'],
            "address": row['address'],
            "image": image_src,
            "deleted_at": deleted_at
        }
        return jsonify({"status": "success", "message": "删除成功", "employee": deleted_employee}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": "数据库错误"}), 500


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
        print("数据库已初始化。")
    app.run(host='0.0.0.0', port=5000, debug=True)
