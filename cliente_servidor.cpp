// Archivo: cliente_sensor.cpp (Versión para Linux/WSL)
#include <iostream>
#include <sys/socket.h> // Para sockets en Linux
#include <arpa/inet.h>  // Para inet_pton
#include <unistd.h>     // Para close() y sleep()
#include <cstdint>
#include <string>
#include <vector>
#include <ctime>
#include <cstring>
#include <openssl/sha.h>

// --- Configuración (idéntica) ---
const char* SERVER_IP = "127.0.0.1";
const int SERVER_PORT = 12345;
const int SENSOR_ID = 101;
const int SEND_INTERVAL_S = 5;

// --- Estructura de Datos (idéntica) ---
#pragma pack(push, 1)
struct SensorData {
    int16_t id;
    uint32_t timestamp;
    float temperatura;
    float presion;
    float humedad;
    char signature[65];
};
#pragma pack(pop)

// --- Funciones de Criptografía
std::string calculate_sha256_stub(const char* data, size_t len) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, data, len);
    SHA256_Final(hash, &sha256);

    char outputBuffer[65];
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(outputBuffer + (i * 2), "%02x", hash[i]);
    }
    outputBuffer[64] = 0;
    return std::string(outputBuffer);
}

void xor_encrypt_decrypt(char* data, size_t len) {
    const std::string key = "miClaveSecretaSuperLarga";
    for (size_t i = 0; i < len; ++i) {
        data[i] ^= key[i % key.length()];
    }
}

int main() {
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == -1) {
        std::cerr << "Error al crear el socket" << std::endl;
        return 1;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &serverAddr.sin_addr);

    if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        std::cerr << "No se pudo conectar al servidor" << std::endl;
        close(clientSocket);
        return 1;
    }

    std::cout << "Conectado al servidor en " << SERVER_IP << ":" << SERVER_PORT << std::endl;

    while (true) {
        SensorData packet;
        packet.id = SENSOR_ID;
        packet.timestamp = static_cast<uint32_t>(time(nullptr));
        packet.temperatura = 20.0f + (rand() % 150) / 10.0f;
        packet.presion = 1000.0f + (rand() % 200) / 10.0f;
        packet.humedad = 40.0f + (rand() % 300) / 10.0f;

        size_t data_to_sign_len = sizeof(SensorData) - sizeof(packet.signature);
        std::string hash = calculate_sha256_stub((char*)&packet, data_to_sign_len);
        strncpy(packet.signature, hash.c_str(), sizeof(packet.signature) -1);
        packet.signature[sizeof(packet.signature)-1] = '\0';

        std::cout << "\n--- Enviando nuevo paquete ---" << std::endl;
        std::cout << "ID: " << packet.id << ", Temp: " << packet.temperatura << std::endl;
        
        xor_encrypt_decrypt((char*)&packet, sizeof(SensorData));
        
        if (send(clientSocket, (char*)&packet, sizeof(SensorData), 0) < 0) {
            std::cerr << "send falló" << std::endl;
            break;
        }

        std::cout << sizeof(SensorData) << " bytes enviados al servidor." << std::endl;
        sleep(SEND_INTERVAL_S);
    }

    close(clientSocket);
    return 0;
}