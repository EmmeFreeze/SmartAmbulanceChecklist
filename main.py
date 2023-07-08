import sqlite3
import json
from flask import Flask, jsonify
from flask_cors import CORS
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'storage/checklist.db')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/checklist')
def get_checklist():
    if(not os.path.exists(db_path)):
        print("Database non trovato")
        return jsonify({'error': 'Database non trovato'})
    
    conn = sqlite3.connect(db_path)

    # Creazione del cursore per eseguire le query
    cur = conn.cursor()

    # Query per ottenere le macro posizioni
    cur.execute('SELECT macro_posizione_id, nome_macro_posizione FROM MacroPosizioni')
    macro_posizioni = cur.fetchall()

    # Lista di macro posizioni nel formato richiesto dal JSON
    macro_locations = []

    # Ciclo per ottenere le posizioni e gli oggetti per ogni macro posizione
    for macro_posizione in macro_posizioni:
        macro_posizione_id, macro_posizione_nome = macro_posizione
        macro_location = {
            'macro_location_name': macro_posizione_nome,
            'locations': []
        }

        # Query per ottenere le posizioni per la macro posizione corrente
        cur.execute('SELECT posizione_id, nome_posizione FROM Posizioni WHERE macro_posizione_id = ?', (macro_posizione_id,))
        posizioni = cur.fetchall()

        # Ciclo per ottenere gli oggetti per ogni posizione
        for posizione in posizioni:
            posizione_id, posizione_nome = posizione
            location = {
                'location_name': posizione_nome,
                'location_objects': []
            }

            # Query per ottenere gli oggetti per la posizione corrente
            cur.execute('SELECT nome_oggetto, quantita FROM Oggetti WHERE posizione_id = ?', (posizione_id,))
            oggetti = cur.fetchall()

            # Ciclo per aggiungere gli oggetti alla lista di oggetti della posizione corrente
            for oggetto in oggetti:
                oggetto_nome, oggetto_quantita = oggetto
                location['location_objects'].append({
                    'object_name': oggetto_nome,
                    'object_quantity': oggetto_quantita
                })

            # Aggiunta della posizione corrente alla lista di posizioni della macro posizione corrente
            macro_location['locations'].append(location)

        # Aggiunta della macro posizione corrente alla lista di macro posizioni
        macro_locations.append(macro_location)

    # Chiusura della connessione al database
    conn.close()

    # Creazione del JSON
    data = {'macro_locations': macro_locations}

    # Restituzione del JSON come risposta alla richiesta HTTP
    return jsonify(data)

# render html page for the frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=80)