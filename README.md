# PFO 2: Sistema de Gestión de Tareas con API y Persistencia SQLite

Sistema cliente-servidor desarrollado con Flask y SQLite que implementa una API REST con autenticación segura, persistencia relacional y un cliente interactivo por consola (CLI).

---

## 1. Alcance y Arquitectura del Proyecto

El sistema está dividido en dos capas principales:
- **Servidor (API REST + Web):** Expone endpoints protegidos para registro, login y gestión de tareas, empleando hasheo criptográfico robusto (Scrypt vía Werkzeug) y encapsulamiento de datos mediante el patrón Repositorio (OOP).
- **Cliente (CLI interactivo):** Aplicación de terminal que consume la API mediante peticiones HTTP autenticadas (Basic Auth / Session cookies) con la librería `requests`.

### Estructura de Directorios

```text
pfo2_proyecto/
│
├── servidor/
│   ├── app.py                 # Configuración Flask y ruteo de endpoints
│   ├── db.py                  # Conexión por request y setup de SQLite
│   ├── repositorios.py        # Patrón Repositorio (acceso a datos)
│   ├── auth.py                # Decoradores y validación de credenciales
│   └── templates/
│       └── tareas.html        # Vista HTML de bienvenida (GET /tareas)
│
├── cliente/
│   └── cliente.py             # Cliente de terminal interactivo
│
├── docs/                      # Archivos para GitHub Pages y capturas
│   ├── index.html
│   └── capturas/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 2. Contrato de la API (Especificación de Endpoints)

| Método | Endpoint | Autenticación | Entrada (Payload) | Código Éxito | Respuesta / Comportamiento |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/registro` | No | `{"usuario": "...", "contraseña": "..."}` | `201 Created` | Registra usuario con hash seguro. `400` por validación, `409` si existe. |
| `POST` | `/login` | No | `{"usuario": "...", "contraseña": "..."}` | `200 OK` | Valida credenciales e inicia sesión HTTP (cookie). `401` si falla. |
| `POST` | `/logout` | Sí | Vacío | `200 OK` | Cierra la sesión activa. |
| `GET` | `/tareas` | Sí | Ninguno | `200 OK` | Devuelve HTML de bienvenida con listado de tareas asignadas al usuario. |
| `GET` | `/api/tareas` | Sí | Ninguno | `200 OK` | Devuelve JSON con lista de tareas: `[{"id": 1, "titulo": "...", "completada": 0}]`. |
| `POST` | `/api/tareas` | Sí | `{"titulo": "..."}` | `201 Created` | Crea una nueva tarea asociada al usuario autenticado. |

---

## 3. Instalación y Puesta en Marcha (Entorno Local)

### 3.1. Clonar el repositorio y preparar entorno
```bash
# Clonar repositorio
git clone <URL_DE_TU_REPOSITORIO>
cd pfo2_proyecto

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3.2. Ejecutar el Servidor
```bash
python -m servidor.app
# El servidor iniciará en http://127.0.0.1:5000/
```

### 3.3. Ejecutar el Cliente CLI
```bash
python -m cliente.cliente
```

---

## 4. Respuestas Conceptuales

### ¿Por qué hashear contraseñas?
> *Sección en desarrollo: Se documentará el uso de algoritmos lentos (Scrypt/Bcrypt), el rol de los factores de costo (memoria/CPU) contra ataques de fuerza bruta mediante GPU, y la necesidad del Salt aleatorio para invalidar ataques por tablas arcoíris.*

### Ventajas de usar SQLite en este proyecto
> *Sección en desarrollo: Se documentará su naturaleza serverless, portabilidad en un único archivo de disco, cero configuración y suficiencia transaccional (ACID) para sistemas mono-instancia o entornos de desarrollo.*

---

## 5. Capturas de Pruebas y Enlace de Despliegue
- **GitHub Pages:** *(Enlace pendiente de configuración en rama gh-pages o carpeta docs/)*
- **Evidencias de ejecución:** *(A incorporar al completar las pruebas del cliente CLI)*