"""
/front/messages/<user_id> builds a html page to see messages
"""
VERSION = "12"

import json
from datetime import datetime as DateTime
import requests
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy.sql import or

## usual Flask initilization
app = Flask(__name__)

## DB declaration

# filename where to store stuff (sqlite is file-based)
db_name = 'chat.db'
# how do we connect to the database ?
# here we say it's by looking in a file named chat.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

## define a table in the database

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    nickname = db.Column(db.String)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime)
    # Define relationships (to fetch User objects directly)
    author = db.relationship('User', foreign_keys=[author_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

@app.route('/')
def hello_world():
    return f'hello, this is a chat app! (version {VERSION})'
  # redirect to /front/users
    # actually this is just a rsponse with a 301 HTTP code
    return redirect('/front/users')

# try it with
"""
http :5001/db/alive
"""
@app.route('/db/alive')
def db_alive():
    try:
        result = db.session.execute(text('SELECT 1'))
        print(result)
        return dict(status="healthy", message="Database connection is alive")
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


# try it with
"""
http :5001/api/version
"""
@app.route('/api/version')
def version():
    return dict(version=VERSION)

# try it with
"""
http :5001/api/users
"""
@app.route('/api/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return [dict(
            id=user.id, name=user.name, email=user.email, nickname=user.nickname)
        for user in users]

# try it with
"""
http :5001/api/users/1
"""
@app.route('/api/users/<int:id>', methods=['GET'])
def list_user(id):
    try:
        # as id is the primary key
        user = User.query.get(id)
        return dict(
            id=user.id, name=user.name, email=user.email, nickname=user.nickname)
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422
    
# try it with
"""
http :5001/api/messages
"""
@app.route('/api/messages', methods=['GET'])
def list_messages():
    messages = Message.query.all()
    return [dict(
            id=message.id, content=message.content, date=message.date,
            author_id=message.author_id, recipient_id=message.recipient_id)
        for message in messages]

# try it with
"""
http :5001/api/messages/with/1
"""

@app.route('/api/messages/with/<int:recipient_id>', methods=['GET'])
def list_messages_to(recipient_id):
     """
    returns only messages to and from a given person
    need to write a little more elaborate query
    we still can only return author_id and recipient_id
        
        
        
        
    # try it with
"""

@app.route('/api/messages', methods=['POST'])
def create_message():
    try:
        parameters = json.loads(request.data)
        content = parameters['content']
        author_id = parameters['author_id']

 
    ## Frontend
# for clarity we define our routes in the /front namespace
# however in practice /front/users would probably be just /users

# try it by pointing your browser to
"""
http://localhost:5001/front/users
"""
@app.route('/front/users')
def front_users():


# try it with
@app.route('/api/users', methods=['POST'])
def create_user():
    # we expect the user to send a JSON object
    # with the 3 fields name email and nickname
    try:
        parameters = json.loads(request.data)
        name = parameters['name']
        email = parameters['email']
        nickname = parameters['nickname']
        print("received request to create user", name, email, nickname)
        # temporary
# try it by pointing your browser to
"""
http://localhost:5001/front/messages/1
"""
@app.route('/front/messages/<int:recipient>')
def front_messages(recipient):
    # same as for the users, let's pretend we don't have direct access to the DB
    url = request.url_root + f'/api/users/{recipient}'
    req1 = requests.get(url)
    if not (200 <= req1.status_code < 300):
        return dict(error="could not request user info", url=url,
                    status=req1.status_code, text=req1.text)
    user = req1.json()
    req2 = requests.get(request.url_root + f'/api/messages/with/{recipient}')
    if not (200 <= req2.status_code < 300):
        return dict(error="could not request messages list", url=url,
                    
if __name__ == '__main__':
    app.run()