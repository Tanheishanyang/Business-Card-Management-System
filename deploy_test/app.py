from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template("Welcome/Welcome.html")

@app.route('/register')
def register():
    return render_template("Register/Register.html") 

@app.route('/home')  # 添加新路由
def home():
    return render_template("Home/Home.html")

if __name__ == '__main__':
    app.run(host='::', port=80, debug=True)
