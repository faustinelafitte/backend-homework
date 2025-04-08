from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

@app.route('/')
def home():
    return "hello, this is a chat app!"

@app.route('/db/alive')
def db_alive():
    try:
        db.session.execute('SELECT 1')
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "details": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)

