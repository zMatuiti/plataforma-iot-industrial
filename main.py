import sqlite3

# Nombre del archivo de la base de datos
db_file = 'industrial_data.db'

try:
    # 1. Conectar a la base de datos (se crea si no existe)
    conn = sqlite3.connect(db_file)
    print(f"Conexión exitosa a la base de datos '{db_file}'")

    # 2. Crear un objeto cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # 3. Definir y ejecutar el comando para crear la tabla
    # Se usa "IF NOT EXISTS" para evitar errores si el script se ejecuta varias veces.
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

    # 4. Guardar (confirmar) los cambios
    conn.commit()

except sqlite3.Error as e:
    print(f"Error al conectar o configurar la base de datos: {e}")

finally:
    # 5. Cerrar la conexión
    if conn:
        conn.close()
        print("Conexión a la base de datos cerrada.")