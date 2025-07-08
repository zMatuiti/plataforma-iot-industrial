import sqlite3

db_file = 'industrial_data.db'

try:
    conn = sqlite3.connect(db_file)
    print(f"Conexión exitosa a la base de datos '{db_file}'")

    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            temperatura REAL,
            presion REAL,
            humedad REAL
        )
    ''')
    print("Tabla 'lecturas' creada o ya existente.")

    conn.commit()

except sqlite3.Error as e:
    print(f"Error al conectar o configurar la base de datos: {e}")

finally:
    if conn:
        conn.close()
        print("Conexión a la base de datos cerrada.")