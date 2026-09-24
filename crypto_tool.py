#!/usr/bin/env python3
"""
crypto_tool.py
BCY0010 - Evaluación Formativa 2: Encargo individual
Fundamentos de Blockchain - Paquete básico de encriptación con PyCryptodome

Alumno: Cristobal Altamirano

Este programa cumple con los requisitos funcionales:
RF-01: Recibir como input un archivo de texto plano (máximo 1 KB).
RF-02: Generar una llave criptográfica válida para el algoritmo AES.
RF-03: Cifrar el contenido del archivo y devolver el texto cifrado (ciphertext).
RF-04: Descifrar el texto cifrado utilizando la misma llave, recuperando el texto original.
RF-05: Ejecutarse completamente desde la línea de comandos (CLI).

Modo AES seleccionado: AES-256 en modo CBC (Cipher Block Chaining).
Justificación del modo: CBC es un modo ampliamente soportado y didáctico para
introducir los conceptos de Vector de Inicialización (IV) y padding, que son
la base para entender por qué blockchain necesita mecanismos de integridad
(hash, Merkle Tree) para detectar cualquier alteración de un dato.
Tamaño de llave: 32 bytes (256 bits), el nivel más alto soportado por AES.
"""

import os
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# ---------------------------------------------------------------------------
# Generación de llave
# ---------------------------------------------------------------------------
def generar_llave(ruta_llave="llave.key"):
    """
    Genera una llave AES-256 (32 bytes = 256 bits) aleatoria y segura
    usando get_random_bytes(), y la guarda en un archivo binario para
    que pueda reutilizarse en cifrados/descifrados posteriores.
    """
    llave = get_random_bytes(32)  # 256 bits
    with open(ruta_llave, "wb") as f:
        f.write(llave)
    print(f"Llave generada: {llave.hex()}")
    print(f"Tamaño: {len(llave) * 8} bits")
    print(f"Guardada en: {ruta_llave}")
    return llave


# ---------------------------------------------------------------------------
# Cifrado
# ---------------------------------------------------------------------------
def cifrar(texto_plano, llave):
    """
    Cifra un texto plano usando AES-256 en modo CBC.
    Genera un IV aleatorio distinto en cada llamada (para que el mismo texto
    plano nunca produzca el mismo ciphertext dos veces), aplica padding
    PKCS7 y retorna IV + ciphertext codificados en base64 para que el
    resultado sea un archivo de texto seguro de manipular.
    """
    if isinstance(texto_plano, str):
        texto_plano = texto_plano.encode("utf-8")

    # Generar IV aleatorio de 16 bytes (tamaño de bloque de AES)
    iv = get_random_bytes(AES.block_size)  # 16 bytes

    # Crear cifrador AES en modo CBC
    cifrador = AES.new(llave, AES.MODE_CBC, iv)

    # Aplicar padding y cifrar
    texto_padded = pad(texto_plano, AES.block_size)
    ciphertext = cifrador.encrypt(texto_padded)

    # Concatenar IV + ciphertext y codificar en base64
    resultado = base64.b64encode(iv + ciphertext)

    print(f"IV: {iv.hex()}")
    print(f"Ciphertext ({len(ciphertext)} bytes): {ciphertext.hex()[:64]}...")

    return resultado


# ---------------------------------------------------------------------------
# Descifrado
# ---------------------------------------------------------------------------
def descifrar(datos_cifrados, llave):
    """
    Descifra datos cifrados con AES-256 CBC.
    Espera un blob en base64 que contiene IV (primeros 16 bytes) +
    ciphertext (el resto). Retorna el texto plano original ya
    decodificado en utf-8.
    """
    datos_raw = base64.b64decode(datos_cifrados)

    # Extraer IV (primeros 16 bytes) y ciphertext (resto)
    iv = datos_raw[:AES.block_size]
    ciphertext = datos_raw[AES.block_size:]

    # Crear descifrador con la misma llave y el IV recuperado
    descifrador = AES.new(llave, AES.MODE_CBC, iv)

    # Descifrar y quitar el padding
    texto_padded = descifrador.decrypt(ciphertext)
    texto_plano = unpad(texto_padded, AES.block_size)

    return texto_plano.decode("utf-8")


# ---------------------------------------------------------------------------
# Operaciones sobre archivos
# ---------------------------------------------------------------------------
def cifrar_archivo(ruta_entrada, ruta_salida, llave):
    """Cifra un archivo de texto plano (máx. 1 KB) y guarda el resultado."""
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        contenido = f.read()

    # RF-01: validar tamaño máximo de 1 KB
    if len(contenido.encode("utf-8")) > 1024:
        print("Error: El archivo excede 1 KB.")
        return None

    resultado = cifrar(contenido, llave)
    with open(ruta_salida, "wb") as f:
        f.write(resultado)

    print(f"Archivo cifrado guardado en: {ruta_salida}")
    return resultado


def descifrar_archivo(ruta_entrada, ruta_salida, llave):
    """Descifra un archivo previamente cifrado con este mismo programa."""
    with open(ruta_entrada, "rb") as f:
        datos = f.read()

    texto = descifrar(datos, llave)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"Archivo descifrado guardado en: {ruta_salida}")
    return texto


# ---------------------------------------------------------------------------
# Interfaz de línea de comandos (RF-05)
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python crypto_tool.py generar")
        print("  python crypto_tool.py cifrar <archivo_entrada> <archivo_salida>")
        print("  python crypto_tool.py descifrar <archivo_entrada> <archivo_salida>")
        return

    comando = sys.argv[1].lower()

    if comando == "generar":
        generar_llave()

    elif comando == "cifrar":
        if len(sys.argv) != 4:
            print("Uso: python crypto_tool.py cifrar <entrada> <salida>")
            return
        if not os.path.exists("llave.key"):
            print("Error: no existe llave.key. Ejecuta primero 'generar'.")
            return
        with open("llave.key", "rb") as f:
            llave = f.read()
        cifrar_archivo(sys.argv[2], sys.argv[3], llave)

    elif comando == "descifrar":
        if len(sys.argv) != 4:
            print("Uso: python crypto_tool.py descifrar <entrada> <salida>")
            return
        if not os.path.exists("llave.key"):
            print("Error: no existe llave.key.")
            return
        with open("llave.key", "rb") as f:
            llave = f.read()
        descifrar_archivo(sys.argv[2], sys.argv[3], llave)

    else:
        print(f"Comando no reconocido: {comando}")


if __name__ == "__main__":
    main()
