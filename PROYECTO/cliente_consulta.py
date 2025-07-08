import requests
import time

API_URL = 'http://127.0.0.1:5001/api/lecturas'
LIMITE_TEMPERATURA = 30.0 # este es el limite para que salte la alerta

while True:
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            lecturas = response.json()
            if lecturas:
                # revisa la lectura mas reciente
                ultima_lectura = lecturas[0]
                temp = ultima_lectura['temperatura']
                print(f"Temperatura -> {temp:.2f}°C")

                if temp > LIMITE_TEMPERATURA:
                    print(f"ALERTA: ¡Temperatura alta detectada! -> {temp:.2f}°C")
        else:
            print(f"Error al consultar la API: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("No se puede conectar al Servidor Final. Reintentando...")

    time.sleep(10) # espera 10 segundos para la proxima consulta