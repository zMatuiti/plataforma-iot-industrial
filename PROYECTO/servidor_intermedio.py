import socket
import sqlite3
import struct
import time
import requests
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
    return hashlib.sha256(data).hexdigest()

def handle_client(conn, addr):
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
            signature_received = unpacked_data[5].decode(
                'utf-8').rstrip('\x00')

            # Convertir timestamp a formato legible
            timestamp_str = datetime.utcfromtimestamp(
                ts_unix).strftime('%Y-%m-%d %H:%M:%S')

            print(
                f"Datos desencriptados: ID={sensor_id}, Temp={temperatura:.2f}, Pres={presion:.2f}, Hum={humedad:.2f}")
            print(
                f"Timestamp: {timestamp_str}, Firma: {signature_received[:10]}...")

            # 4. Validar la firma
            data_to_sign = struct.pack(
                '<hIfff', sensor_id, ts_unix, temperatura, presion, humedad)
            expected_hash = calculate_sha256(data_to_sign)

            if expected_hash == signature_received:
                print("Firma del paquete verificada.")
                # 5. Formatear y reenviar al Servidor Final
                payload = {
                    "sensor_id": sensor_id,
                    "timestamp": timestamp_str,
                    "temperatura": temperatura,
                    "presion": presion,
                    "humedad": humedad
                }
                try:
                    response = requests.post(
                        'http://127.0.0.1:5001/api/lecturas', json=payload)
                    if response.status_code == 201:
                        print("Datos reenviados exitosamente al Servidor Final.")
                    else:
                        print(
                            f"Error al reenviar datos: {response.status_code}")
                except requests.exceptions.ConnectionError as e:
                    print(f"No se pudo conectar con el Servidor Final: {e}")
            else:
                print(
                    f"ALERTA DE SEGURIDAD: La firma del paquete no coincide. Paquete descartado.")

    except ConnectionResetError:
        print(f"Conexión con {addr} cerrada abruptamente.")
    finally:
        conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    main()
