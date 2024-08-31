import socket
import binascii
import random

def calculate_crc(message):
    """
    Calcula el valor CRC del mensaje dado.
    Args:
    - message (str): El mensaje a calcular el CRC.
    
    Returns:
    - int: El valor CRC del mensaje.
    """
    crc = binascii.crc32(message.encode('utf-8'))
    return crc

def hamming_distance(str1, str2):
    """
    Calcula la distancia de Hamming entre dos cadenas de igual longitud.
    Args:
    - str1 (str): La primera cadena.
    - str2 (str): La segunda cadena.
    
    Returns:
    - int: La distancia de Hamming entre las dos cadenas.
    """
    if len(str1) != len(str2):
        raise ValueError("Las cadenas deben tener la misma longitud")
    return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))

def introduce_errors(message, error_percentage):
    """
    Introduce errores aleatorios en el mensaje según el porcentaje de error.
    Args:
    - message (str): El mensaje original.
    - error_percentage (float): El porcentaje de errores a introducir.
    
    Returns:
    - str: El mensaje con errores introducidos.
    """
    message = list(message)
    num_errors = int(len(message) * error_percentage / 100)
    for _ in range(num_errors):
        index = random.randint(0, len(message) - 1)
        message[index] = chr(random.randint(32, 126))
    return ''.join(message)

def main():
    host = 'localhost'
    port = 12345

    # Crear el socket del servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Servidor escuchando en {host}:{port}")
        
        while True:
            conn, addr = s.accept()
            print(f"Conectado por {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = data.decode('utf-8')
                    if data.lower() == "terminar":
                        print("Terminando conexión...")
                        break

                    # Procesar el mensaje recibido
                    message_with_crc, error_percentage = data.split('|')
                    message, received_crc = message_with_crc.rsplit(':', 1)
                    error_percentage = float(error_percentage)
                    received_crc = int(received_crc)
                    print(f"Mensaje recibido: {message}")
                    print(f"CRC recibido: {received_crc}")
                    print(f"Porcentaje de error: {error_percentage}")

                    # Calcular el CRC del mensaje recibido
                    calculated_crc = calculate_crc(message)
                    print(f"Valor CRC calculado: {calculated_crc}")

                    # Introducir errores en el mensaje y calcular el CRC del mensaje con errores
                    error_message = introduce_errors(message, error_percentage)
                    error_message_crc = calculate_crc(error_message)
                    print(f"CRC del mensaje con errores: {error_message_crc}")

                    # Comparar CRC del mensaje recibido y el CRC del mensaje con errores
                    crc_match = received_crc == error_message_crc
                    print(f"CRC coincide: {crc_match}")

                    # Calcular la distancia de Hamming entre el mensaje original y el mensaje con errores
                    distance = hamming_distance(message, error_message)
                    print(f"Distancia de Hamming: {distance}")

                    # Enviar la respuesta al cliente
                    response = (f"CRC recibido: {received_crc}\n"
                                f"CRC mensaje con errores: {error_message_crc}\n"
                                f"CRC coincide: {crc_match}\n"
                                f"Mensaje con error: {error_message}\n"
                                f"Distancia de Hamming: {distance}")
                    conn.sendall(response.encode('utf-8'))
                print(f"Conexión terminada con {addr}")

if __name__ == "__main__":
    main()
