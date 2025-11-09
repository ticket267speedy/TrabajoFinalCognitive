from flask import Flask

app = Flask(__name__)

@app.get('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)