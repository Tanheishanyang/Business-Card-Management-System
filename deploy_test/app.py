from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IPv6 Test</title>
    </head>
    <body>
        <h1>网站部署测试</h1>
        <p>网站通过Ngrok部署</p>
        <p>后续开发人员: cjy, yjx</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='::', port=80, debug=True)