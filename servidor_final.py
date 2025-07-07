from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_FILE = 'industrial_data.db'

# Endpoint para recibir datos del servidor intermedio
@app.route('/api/lecturas', methods=['POST'])
def add_lectura():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lecturas (sensor_id, timestamp, temperatura, presion, humedad) VALUES (?, ?, ?, ?, ?)",
            (data['sensor_id'], data['timestamp'], data['temperatura'], data['presion'], data['humedad'])
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para que el cliente de consulta y el dashboard pidan datos
@app.route('/api/lecturas', methods=['GET'])
def get_lecturas():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecturas ORDER BY timestamp DESC LIMIT 20")
    lecturas = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in lecturas])

# Endpoint para mostrar el dashboard web
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    # Ejecuta este servidor en un puerto diferente, ej. 5001
    app.run(host='0.0.0.0', port=5001, debug=True)