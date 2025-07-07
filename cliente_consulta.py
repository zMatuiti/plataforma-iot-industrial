import requests
import time

API_URL = 'http://127.0.0.1:5001/api/lecturas'
UMBRAL_TEMPERATURA = 30.0 # Define tu umbral de alerta

while True:
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            lecturas = response.json()
            if lecturas:
                # Revisa la lectura más reciente
                ultima_lectura = lecturas[0]
                temp = ultima_lectura['temperatura']
                print(f"Última lectura: Temp={temp:.2f}°C")

                if temp > UMBRAL_TEMPERATURA:
                    print(f"🚨 ALERTA: ¡Temperatura alta detectada! -> {temp:.2f}°C 🚨")
        else:
            print(f"Error al consultar la API: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("No se puede conectar al Servidor Final. Reintentando...")

    time.sleep(10) # Espera 10 segundos para la próxima consulta