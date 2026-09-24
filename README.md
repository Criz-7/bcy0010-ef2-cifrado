[README.md](https://github.com/user-attachments/files/32590970/README.md)
# crypto_tool.py — Encriptador AES-256 con PyCryptodome

**Asignatura:** BCY0010 – Fundamentos de Blockchain
**Evaluación:** Formativa N°2 — Encargo individual
**Alumno/a:** [Tu nombre]

## 1. Descripción

Paquete básico de encriptación de archivos de texto plano, desarrollado en Python
con la librería `PyCryptodome`. Implementa generación de llave, cifrado y
descifrado de archivos usando **AES-256 en modo CBC**, ejecutable completamente
desde línea de comandos (CLI).

## 2. Modo AES seleccionado y justificación

- **Algoritmo:** AES (Advanced Encryption Standard)
- **Tamaño de llave:** 256 bits (32 bytes) — el nivel más alto soportado por AES,
  generado con `get_random_bytes(32)` (criptográficamente seguro).
- **Modo de operación:** CBC (Cipher Block Chaining)
- **Justificación:** CBC encadena cada bloque cifrado con el anterior mediante
  un Vector de Inicialización (IV) aleatorio de 16 bytes, lo que evita que un
  mismo texto plano genere siempre el mismo ciphertext. Es un modo estándar,
  ampliamente soportado, y pedagógicamente útil porque obliga a manejar
  explícitamente IV y padding (PKCS7), dos conceptos clave para entender más
  adelante por qué blockchain necesita mecanismos de integridad (hash, árbol
  de Merkle) que detecten cualquier alteración de un dato.

## 3. Instalación

```bash
pip install -r requirements.txt
# o bien
pip install pycryptodome
```

## 4. Uso (CLI)

```bash
# 1. Generar una llave AES-256 y guardarla en llave.key
python crypto_tool.py generar

# 2. Cifrar un archivo de texto plano (máximo 1 KB)
python crypto_tool.py cifrar mensaje_prueba.txt mensaje.enc

# 3. Descifrar el archivo cifrado
python crypto_tool.py descifrar mensaje.enc mensaje_recuperado.txt

# 4. Verificar que el resultado es idéntico al original
diff mensaje_prueba.txt mensaje_recuperado.txt
# Si no muestra nada, los archivos son idénticos
```

## 5. Nota sobre las capturas

> **Importante:** en el entorno donde se redactó este informe no fue posible
> instalar `pycryptodome` (sin acceso a internet), por lo que las capturas de
> ejecución reales (carpeta `capturas/`) deben generarse ejecutando los pasos
> de la sección 4 en tu propio equipo (con Python 3.x y PyCryptodome
> instalado), tal como indica la Guía 1.1.3. La lógica del programa fue
> verificada exitosamente con una librería criptográfica equivalente
> (AES-256-CBC + padding PKCS7), confirmando que cifra y descifra
> correctamente y que el texto recuperado es idéntico al original. Los
> archivos `mensaje.enc` y `mensaje_recuperado.txt` incluidos en este
> repositorio provienen de esa verificación de lógica.

## 6. Respuestas a las preguntas de análisis

**1. ¿Qué sucede si intentas descifrar con una llave diferente a la que se usó
para cifrar?**
El descifrado produce bytes ilegibles (basura) y, en la mayoría de los casos,
`unpad()` lanza una excepción `ValueError: Padding is incorrect`, porque el
padding PKCS7 resultante no es válido. Esto demuestra que sin la llave
correcta es computacionalmente inviable recuperar el texto original.

**2. ¿Por qué el IV debe ser diferente cada vez que ciframos, aunque usemos la
misma llave? ¿Qué pasaría si siempre usamos el mismo IV?**
El IV asegura que, aunque se cifre el mismo texto plano con la misma llave,
el ciphertext resultante sea distinto cada vez (propiedad de semántica de
seguridad). Si se reutilizara siempre el mismo IV, dos mensajes iguales (o con
el mismo prefijo) producirían el mismo patrón de bloques cifrados, filtrando
información sobre el contenido y debilitando la seguridad del esquema CBC.

**3. ¿Cuál es la relación entre el tamaño de la llave y la seguridad del
cifrado? ¿Cuántas combinaciones posibles tiene una llave de 256 bits?**
A mayor tamaño de llave, mayor es el espacio de búsqueda que un atacante de
fuerza bruta debe recorrer. Una llave de 256 bits tiene 2^256 combinaciones
posibles (~1.15 × 10^77), un número tan grande que un ataque de fuerza bruta
es inviable incluso con la capacidad de cómputo actual o futura previsible.

**4. ¿Por qué se necesita padding? ¿Qué tamaño tiene un bloque AES y qué pasa
si el texto plano no es múltiplo de ese tamaño?**
AES es un cifrado por bloques de 16 bytes (128 bits): solo puede cifrar datos
cuya longitud sea múltiplo exacto de 16 bytes. Si el texto plano no lo es, se
agrega padding (relleno) —en este caso PKCS7— para completar el último bloque.
Al descifrar, `unpad()` elimina ese relleno para recuperar el tamaño original.

**5. ¿Por qué se utiliza base64 para almacenar el resultado? ¿Cuál es la
diferencia entre guardar bytes crudos y base64?**
El ciphertext es una secuencia de bytes binarios que puede contener valores no
imprimibles. Base64 codifica esos bytes en un conjunto de 64 caracteres ASCII
seguros de manipular, copiar, pegar o transmitir por canales de texto (correo,
JSON, terminal) sin riesgo de corrupción. La diferencia frente a guardar bytes
crudos es que base64 aumenta el tamaño (~33%) a cambio de portabilidad y
legibilidad como texto.

**6. ¿Cómo se relaciona este cifrado simétrico con el problema del doble
gasto y la confianza que analizaste en la dinámica de compraventa?**
El cifrado simétrico protege la **confidencialidad** de la información (que
solo quien tiene la llave pueda leerla), pero por sí solo no resuelve el
problema del doble gasto ni garantiza **integridad** o **autenticidad**. El
doble gasto se resuelve con mecanismos de consenso distribuido y con
estructuras como el árbol de Merkle y las firmas digitales (criptografía
asimétrica), que permiten verificar que un dato no fue alterado y que
proviene realmente de quien dice haberlo emitido. El cifrado simétrico es un
primer bloque de la confianza digital, pero necesita combinarse con hashing y
firmas digitales (vistos en la Guía 1.1.3 y en el Ítem 3 de la EP1) para
sostener un sistema como blockchain.

## 7. Estructura de archivos entregados

```
├── crypto_tool.py          # Programa principal (generar / cifrar / descifrar)
├── requirements.txt        # Dependencia: pycryptodome
├── README.md                # Este archivo
├── mensaje_prueba.txt       # Archivo de texto de prueba (< 1 KB)
├── mensaje.enc               # Archivo cifrado de ejemplo
├── mensaje_recuperado.txt   # Archivo descifrado de verificación
└── capturas/                 # Screenshots de ejecución (a completar localmente)
```
