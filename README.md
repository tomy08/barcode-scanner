# Sistema de Escaneo de Códigos de Barras

Sistema web profesional desarrollado para el escaneo y registro unificado de códigos de barras (y QR), cumpliendo de manera estricta con el modelo de calidad de software establecido por la norma **ISO/IEC 25010 (SQuaRE)**.

## 📌 Arquitectura y Tecnologías

- **Backend:** Python + FastAPI
- **Base de Datos:** SQLite + SQLAlchemy (Mapeo Objeto-Relacional ORM)
- **Motor de Escaneo:** `zxing-cpp` (Zebra Crossing en C++) con `OpenCV`.
- **Frontend:** Jinja2 (HTML5 / CSS / Vanilla JS asincrónico puro).

---

## 🛠️ Justificación de Decisiones Técnicas

A fin de cumplir con altos estándares de fiabilidad y usabilidad, se han tomado decisiones arquitectónicas clave durante el desarrollo:

### 1. ¿Por qué NO usar un escáner en vivo desde el navegador?

En las versiones iniciales se evaluó utilizar `getUserMedia` (JavaScript) para leer la cámara en vivo directamente en una etiqueta `<video>`. Sin embargo, esto generaba dos problemas críticos de **Fiabilidad (SQuaRE)**:

- **Falta de Autoenfoque (Autofocus):** Los navegadores móviles bloquean o no implementan correctamente el autoenfoque en vivo del hardware mediante APIs de MediaDevices. Esto provoca que códigos en latas, frascos o espacios pequeños se vean borrosos.
- **Compresión excesiva del Canvas:** Para enviar imágenes asincrónicas en milisegundos se devaluaba la captura de pixeles.
  > **Solución Adoptada (Fiabilidad y Portabilidad):** Se utilizó un acceso de archivo nativo con `capture="environment"`. Al presionar el botón "Abrir Cámara", se abre la **Aplicación Oficial del Celular**, la cual cuenta con HDR, autoenfoque inteligente y macro. Esto dispara la tasa de éxito de lectura casi a un `100%` en condiciones reales y elimina las incompatibilidades de navegadores.

### 2. ¿Por qué usar `zxing-cpp` en lugar de `pyzbar`?

Las primeras pruebas incluyeron `pyzbar` como motor de decodificación. Al ponerlo en práctica, presentaba un grave de déficit en **Eficiencia de Desempeño**:

- `pyzbar` falla estrepitósamente con reflejos blancos intensos (como el de los envases metálicos) o ante códigos torcidos/curvados.
  > **Solución Adoptada:** Se reemplazó por la integración de `zxing-cpp` (Zebra Crossing original portado de C++ para Google). Este es, a día de hoy, el motor _open-source_ más sofisticado, tolerante a curvas, brillo e imágenes cortadas, alineándose con el requerimiento de calidad industrial para escaneos hostiles.

### 3. ¿Por qué incluir `OpenCV` en las imágenes de entrada?

Cuando el frontend sube la foto en Full-HD desde el celular, podría ocasionar el colapso de la red o consumir toda la RAM del backend analizando foto por foto.

> **Solución Adoptada (Mantenibilidad & Eficiencia):** Cuando la imagen llega, OpenCV la lee mágicamente a nivel binario en un Buffer, calcula su proporción y, si supera el estándar óptimo de los `1920 píxeles`, la redimensiona equitativamente antes de que actúe el escáner. Esto salva el servidor de colapsos, acelerando la lectura de milisegundos usando matrices numéricas nativas en C (NumPy).

### 4. Base de Datos Local - SQLite

> **Decisión (Seguridad y Mantenibilidad):** El entorno utiliza Python puro con `SQLAlchemy` como ORM, acoplado a una base local `SQLite`. Esto reduce drásticamente el tiempo de configuración (_Zero-Config Database_) sin comprometer la persistencia en disco ni requerir servidores externos en un ambiente de pruebas/producción a mediana escala.

---

## 🚀 Instalación y Despliegue

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar Entorno (Windows)
.venv\Scripts\activate

# 3. Instalar librerías
pip install -r requirements.txt

# 4. Lanzar Servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **Ingreso:** Visitar `http://localhost:8000` en el navegador del equipo, o ingresar a través de la **IP Local (ej: 192.168.1.x:8000)** desde el celular conectado a la misma red Wi-Fi para aprovechar su cámara fotográfica.
