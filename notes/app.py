import json
import requests
import time
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Lock

app = Flask(__name__)
db_name = 'notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
db = SQLAlchemy(app)

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# Synchronisation
last_update_time = time.time()
update_lock = Lock()

@app.route('/')
def test():
    return "mon serveur fonctionne"

@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        parameters = json.loads(request.data)
        title = parameters['title']
        content = parameters['content']
        done = parameters.get('done', None)
        to_bool = lambda x: str(x).lower() in ['true', '1']
        if not title or not content:
            return {"error": "Title and content required"}, 400
        if done is None:
            new_note = Note(title=title, content=content)
        else:
            new_note = Note(title=title, content=content, done=to_bool(done))
        db.session.add(new_note)
        db.session.commit()
        global last_update_time
        with update_lock:
            last_update_time = time.time()
        return {
            "id": new_note.id,
            "title": new_note.title,
            "content": new_note.content,
            "done": new_note.done
        }, 201
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422

@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(id=note.id, title=note.title, content=note.content, done=note.done) for note in notes]

@app.route('/api/notes/<int:note_id>/done', methods=['POST'])
def update_note_done(note_id):
    try:
        parameters = json.loads(request.data)
        done = parameters['done']
        to_bool = lambda x: str(x).lower() in ['true', '1']
        note = Note.query.get(note_id)
        if not note:
            return dict(error="Note not found"), 404
        note.done = to_bool(done)
        db.session.commit()

        global last_update_time
        with update_lock:
            last_update_time = time.time()

        return dict(ok=True)
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422

@app.route('/api/notes/stream')
def notes_stream():
    global last_update_time
    since = float(request.args.get("since", 0))
    timeout = 10
    waited = 0
    interval = 0.5

    while waited < timeout:
        with update_lock:
            if last_update_time > since:
                notes = Note.query.all()
                return jsonify({
                    "notes": [dict(id=n.id, title=n.title, content=n.content, done=n.done) for n in notes],
                    "timestamp": time.time()
                })
        time.sleep(interval)
        waited += interval

    return jsonify({"notes": [], "timestamp": time.time()})

@app.route('/front/notes')
def front_users():
    url = request.url_root + 'api/notes'
    req = requests.get(url)
    if not (200 <= req.status_code < 300):
        return dict(error="could not request notes list", url=url,
                    status=req.status_code, text=req.text)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
