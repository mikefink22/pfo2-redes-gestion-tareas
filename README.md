# PFO 2: Sistema de Gestión de Tareas con API y Persistencia SQLite

Sistema cliente-servidor desarrollado con Flask y SQLite que implementa una API REST con autenticación segura, persistencia relacional y un cliente interactivo por consola (CLI).

---

## 1. Alcance y Arquitectura del Proyecto

El sistema está dividido en dos capas principales:

- **Servidor (API REST + Web):** expone endpoints protegidos para registro, login y gestión de tareas, con hasheo de contraseñas (scrypt vía Werkzeug) y acceso a datos encapsulado con el patrón Repositorio.
- **Cliente (CLI interactivo):** aplicación de terminal que consume la API con `requests`. Usa `requests.Session()` para conservar la cookie de sesión entre peticiones.

### Estructura de directorios

```
├── servidor/
│   ├── app.py              # Configuración Flask y endpoints
│   ├── db.py               # Conexión por request y creación de tablas SQLite
│   ├── repositorios.py     # Patrón Repositorio (acceso a datos)
│   ├── auth.py             # Decorador @login_requerido
│   └── templates/
│       └── tareas.html     # Vista HTML de bienvenida (GET /tareas)
├── cliente/
│   └── cliente.py          # Cliente de terminal interactivo
├── docs/                   # Página estática para GitHub Pages + capturas
│   ├── index.html
│   └── capturas/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 2. Contrato de la API

| Método | Endpoint      | Auth | Entrada                                   | Éxito         | Comportamiento                                                  |
| ------ | ------------- | ---- | ----------------------------------------- | ------------- | --------------------------------------------------------------- |
| `POST` | `/registro`   | No   | `{"usuario": "...", "contraseña": "..."}` | `201 Created` | Registra usuario con hash seguro. `400` validación, `409` si ya existe. |
| `POST` | `/login`      | No   | `{"usuario": "...", "contraseña": "..."}` | `200 OK`      | Valida credenciales e inicia sesión (cookie). `401` si falla.   |
| `POST` | `/logout`     | Sí   | Vacío                                     | `200 OK`      | Cierra la sesión activa.                                        |
| `GET`  | `/tareas`     | Sí   | Ninguna                                   | `200 OK`      | HTML de bienvenida con las tareas del usuario.                  |
| `GET`  | `/api/tareas` | Sí   | Ninguna                                   | `200 OK`      | JSON: `[{"id": 1, "titulo": "...", "completada": 0}]`.          |
| `POST` | `/api/tareas` | Sí   | `{"titulo": "..."}`                       | `201 Created` | Crea una tarea para el usuario autenticado.                     |

Sin sesión válida, los endpoints protegidos responden `401`.

---

## 3. Instalación y puesta en marcha (local)

```bash
git clone https://github.com/mikefink22/pfo2-redes-gestion-tareas.git
cd pfo2-redes-gestion-tareas

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Servidor** (terminal 1):

```bash
python -m servidor.app
# http://127.0.0.1:5000/
```

**Cliente CLI** (terminal 2):

```bash
python -m cliente.cliente
```

> **¿Dónde queda SQLite?** El servidor crea solo el archivo `servidor/tareas.db`
> la primera vez que arranca. No hay que instalar ni configurar nada.
> Está en `.gitignore`, así que no se sube a GitHub.
> Para usar otra ruta: variable de entorno `DB_PATH`.

---

## 4. Despliegue de la API en PythonAnywhere (opcional)

GitHub Pages solo sirve archivos estáticos, así que **no puede ejecutar Flask**.
Para tener la API online se puede usar el plan gratuito de PythonAnywhere:

1. Crear cuenta en pythonanywhere.com y abrir una consola **Bash**.
2. Clonar el repo y crear el entorno:
   ```bash
   git clone https://github.com/mikefink22/pfo2-redes-gestion-tareas.git
   cd pfo2-redes-gestion-tareas
   mkvirtualenv --python=python3.10 venv-tareas
   pip install -r requirements.txt
   ```
3. En la pestaña **Web** → *Add a new web app* → *Manual configuration* (misma versión de Python).
4. En *Virtualenv* poner: `/home/TU_USUARIO/.virtualenvs/venv-tareas`
5. Abrir el archivo WSGI (link en la pestaña Web), borrar su contenido y pegar:
   ```python
   import os
   import sys

   ruta = "/home/TU_USUARIO/pfo2-redes-gestion-tareas"
   if ruta not in sys.path:
       sys.path.insert(0, ruta)

   os.environ["SECRET_KEY"] = "clave-secreta-produccion-tareas"

   from servidor.app import app as application
   ```
6. Botón **Reload**. La API queda en `https://TU_USUARIO.pythonanywhere.com`.
7. El archivo `tareas.db` se crea solo en `~/pfo2-redes-gestion-tareas/servidor/` y persiste entre reinicios.
8. Para que el cliente CLI (que sigue corriendo en tu PC) use la API online:
   ```bash
   # Linux/macOS
   API_URL=https://TU_USUARIO.pythonanywhere.com python -m cliente.cliente
   # Windows (PowerShell)
   $env:API_URL="https://TU_USUARIO.pythonanywhere.com"; python -m cliente.cliente
   ```

---

## 5. Respuestas conceptuales

### ¿Por qué hashear contraseñas?

Si la base de datos se filtra, las contraseñas en texto plano quedan expuestas, y como mucha gente las reutiliza, el daño se extiende a otros servicios. Un hash es una función de un solo sentido: se guarda el resultado y, al hacer login, se hashea lo que escribe el usuario y se compara. Para que sea seguro se usan algoritmos **lentos y costosos** (scrypt, bcrypt, Argon2): scrypt exige mucha memoria y CPU por cada intento, lo que encarece los ataques de fuerza bruta con GPU. Además se agrega un **salt aleatorio** por usuario: dos usuarios con la misma contraseña obtienen hashes distintos y se invalidan los ataques con tablas arcoíris precalculadas. En este proyecto se usa `generate_password_hash(..., method="scrypt")` de Werkzeug, que guarda algoritmo, parámetros y salt dentro del mismo texto.

### Ventajas de usar SQLite en este proyecto

SQLite es una base de datos **sin servidor**: corre dentro del proceso de la aplicación y se guarda en un único archivo, por lo que no requiere instalar, configurar ni administrar un motor aparte. Es portable (se copia el archivo), viene incluida en la librería estándar de Python (`sqlite3`) y ofrece transacciones **ACID**, suficientes para una aplicación de una sola instancia o un entorno de desarrollo y aprendizaje. Su límite es la concurrencia de escritura y la escalabilidad horizontal; para mucho tráfico convendría migrar a PostgreSQL o MySQL, y gracias al patrón Repositorio ese cambio quedaría aislado en `repositorios.py`.

---

## 6. Capturas de pruebas y enlace de despliegue

- **GitHub Pages:** activar en *Settings → Pages → Deploy from a branch → `main` → carpeta `/docs`*. La página queda en `https://mikefink22.github.io/pfo2-redes-gestion-tareas/`.
- **Evidencias:** guardar las capturas del cliente CLI en `docs/capturas/` con los nombres que usa `docs/index.html` (`01-registro.png`, `02-login.png`, `03-crear-tarea.png`, `04-listar-tareas.png`, `05-sin-sesion.png`).
