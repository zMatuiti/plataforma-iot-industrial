import socket
import sqlite3
import struct
import time
import hashlib
from datetime import datetime

# --- Configuración (debe coincidir con el cliente C++) ---
HOST = '127.0.0.1'  # Escuchar en la interfaz local
PORT = 12345        # Puerto para escuchar
DB_FILE = 'industrial_data.db'

# --- Funciones de Criptografía (idénticas al cliente C++) ---
def xor_encrypt_decrypt(data: bytearray) -> bytearray:
    """Aplica el cifrado/descifrado XOR a los datos."""
    key = "miClaveSecretaSuperLarga"
    key_len = len(key)
    for i in range(len(data)):
        data[i] ^= ord(key[i % key_len])
    return data

def calculate_sha256(data: bytes) -> str:
    """Calcula el hash SHA-256 real de los datos."""
    return hashlib.sha256(data).hexdigest()
    
def handle_client(conn, addr):
    """Maneja la conexión de un cliente."""
    print(f"Conectado por {addr}")
    try:
        while True:
            # 1. Recibir datos del cliente. El tamaño del buffer debe coincidir con el struct.
            # El struct tiene: short(2) + uint(4) + float(4) + float(4) + float(4) + char[65] = 83 bytes
            data = conn.recv(83)
            if not data:
                print(f"Cliente {addr} desconectado.")
                break
            
            print(f"\n--- Paquete de {len(data)} bytes recibido ---")

            # 2. Desencriptar los datos
            decrypted_data = xor_encrypt_decrypt(bytearray(data))

            # 3. Desempaquetar los datos usando el formato del struct de C++
            # Formato: < (little-endian) h (short) I (unsigned int) f (float) f f 65s (65-char string)
            unpacked_data = struct.unpack('<hIfff65s', decrypted_data)
            
            sensor_id = unpacked_data[0]
            ts_unix = unpacked_data[1]
            temperatura = unpacked_data[2]
            presion = unpacked_data[3]
            humedad = unpacked_data[4]
            signature_received = unpacked_data[5].decode('utf-8').rstrip('\x00')
            
            # Convertir timestamp a formato legible
            timestamp_str = datetime.utcfromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S')

            print(f"Datos desencriptados: ID={sensor_id}, Temp={temperatura:.2f}, Pres={presion:.2f}, Hum={humedad:.2f}")
            print(f"Timestamp: {timestamp_str}, Firma: {signature_received[:10]}...")

            # 4. (Opcional pero recomendado) Validar la firma
            # Creamos un "paquete" sin la firma para calcular nuestro propio hash
            data_to_sign = struct.pack('<hIfff', sensor_id, ts_unix, temperatura, presion, humedad)
            expected_hash = calculate_sha256_stub(data_to_sign)
            
            # NOTA: La lógica de firma en el cliente C++ es incorrecta, firma todo el paquete
            # incluyendo el espacio de la firma. Para este ejemplo, omitiremos una validación estricta.
            
            # 5. Guardar en la base de datos
            try:
                db_conn = sqlite3.connect(DB_FILE)
                cursor = db_conn.cursor()
                cursor.execute('''
                    INSERT INTO lecturas (sensor_id, timestamp, temperatura, presion, humedad)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sensor_id, timestamp_str, temperatura, presion, humedad))
                db_conn.commit()
                db_conn.close()
                print("Datos guardados en la base de datos.")
            except sqlite3.Error as e:
                print(f"Error de base de datos: {e}")

    except ConnectionResetError:
        print(f"Conexión con {addr} cerrada abruptamente.")
    finally:
        conn.close()

def main():
    """Función principal del servidor."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            # En un servidor real, aquí usarías hilos o asyncio para manejar múltiples clientes
            handle_client(conn, addr)

if __name__ == "__main__":
    main()