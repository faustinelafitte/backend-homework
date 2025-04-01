import pathlib as pl

import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

data = pl.Path(__file__).parent.absolute() / 'data'

# Charger les données CSV
associations_df = pd.read_csv(data / 'associations_etudiantes.csv')
evenements_df = pd.read_csv(data / 'evenements_associations.csv')

## Vous devez ajouter les routes ici : 

@app.route('/')
def bonjour():
    return "Bonjour"

@app.route('/api/alive', methods=['GET'])
def check_alive():
    return jsonify({"message": "Alive"}), 200

@app.route('/api/associations', methods=['GET'])
def id_assos():
    return jsonify(list(associations_df['id'])), 200


@app.route('/api/association/<int:id>', methods=['GET'])
def info_assos(id):
    association = associations_df[associations_df["id"] == id]
    if association.empty:
        return jsonify({"error": "Association not found"}), 404
    return jsonify(association.to_dict(orient='records')[0]), 200


@app.route('/api/evenements', methods=['GET'])
def id_ev():
    return jsonify(list(evenements_df['id'])), 200


@app.route('/api/evenement/<int:id>', methods=['GET'])
def info_ev(id):
    ev = evenements_df[evenements_df["id"] == id]
    if ev.empty:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(ev.to_dict(orient='records')[0]), 200


@app.route('/api/association/<int:id>/evenements', methods=['GET'])
def ev_assos(id):
    evassos = evenements_df[evenements_df["association_id"] == id]
    if evassos.empty:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(list(evassos["nom"])), 200


@app.route('/api/associations/type/<type>', methods=['GET'])
def assos_par_type(type):
    assos = associations_df[associations_df["type"] == type]
    if assos.empty:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(list(assos["nom"])), 200

if __name__ == '__main__':
    app.run(debug=False)
