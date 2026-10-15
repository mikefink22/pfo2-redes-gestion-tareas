"""Cliente de consola interactivo para la API de tareas."""
import getpass
import os

import requests

URL_BASE = os.environ.get("API_URL", "http://127.0.0.1:5000")

# Session guarda la cookie de login automáticamente entre requests.
sesion = requests.Session()


def _mostrar(resp):
    try:
        cuerpo = resp.json()
    except ValueError:
        cuerpo = resp.text[:200]
    print(f"  -> HTTP {resp.status_code}: {cuerpo}")


def _pedir_credenciales():
    usuario = input("Usuario: ").strip()
    contrasena = getpass.getpass("Contraseña: ")
    return {"usuario": usuario, "contraseña": contrasena}


def registrar():
    _mostrar(sesion.post(f"{URL_BASE}/registro", json=_pedir_credenciales()))


def iniciar_sesion():
    _mostrar(sesion.post(f"{URL_BASE}/login", json=_pedir_credenciales()))


def cerrar_sesion():
    _mostrar(sesion.post(f"{URL_BASE}/logout"))


def listar_tareas():
    resp = sesion.get(f"{URL_BASE}/api/tareas")
    if resp.status_code != 200:
        return _mostrar(resp)
    tareas = resp.json()
    if not tareas:
        print("  (no tenés tareas)")
    for t in tareas:
        marca = "x" if t["completada"] else " "
        print(f"  [{marca}] {t['id']}. {t['titulo']}")


def crear_tarea():
    titulo = input("Título de la tarea: ").strip()
    _mostrar(sesion.post(f"{URL_BASE}/api/tareas", json={"titulo": titulo}))


def ver_html():
    resp = sesion.get(f"{URL_BASE}/tareas")
    print(f"  -> HTTP {resp.status_code}")
    if resp.status_code == 200:
        print(resp.text)


OPCIONES = {
    "1": ("Registrarse", registrar),
    "2": ("Iniciar sesión", iniciar_sesion),
    "3": ("Listar mis tareas", listar_tareas),
    "4": ("Crear una tarea", crear_tarea),
    "5": ("Ver página de bienvenida (HTML)", ver_html),
    "6": ("Cerrar sesión", cerrar_sesion),
    "0": ("Salir", None),
}


def main():
    print(f"Cliente de tareas - servidor: {URL_BASE}")
    while True:
        print("\n--- MENÚ ---")
        for clave, (texto, _) in OPCIONES.items():
            print(f"{clave}. {texto}")
        eleccion = input("Elegí una opción: ").strip()
        if eleccion == "0":
            print("¡Hasta luego!")
            break
        accion = OPCIONES.get(eleccion)
        if accion is None:
            print("Opción inválida.")
            continue
        try:
            accion[1]()
        except requests.exceptions.ConnectionError:
            print("  No se pudo conectar al servidor. ¿Está corriendo?")


if __name__ == "__main__":
    main()
