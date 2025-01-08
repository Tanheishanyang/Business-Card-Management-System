from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("Welcome/Welcome.html")

@app.route('/register')
def register():
    return render_template("Register/Register.html") 

@app.route('/login')
def login():
    return render_template("Longin/Login.html") 

if __name__ == '__main__':
    app.run(host='::', port=80, debug=True)
