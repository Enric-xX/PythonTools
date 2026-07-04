import os
import platform
import socket
import requests
import subprocess
import re
import time
from getmac import get_mac_address
from datetime import datetime

def obtener_fabricante(mac):
    """Obtiene el fabricante usando API online + base offline"""
    if mac is None or mac == "No disponible":
        return "Desconocido"
    
    # Intentar API online
    try:
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    
    # Base offline
    oui = mac.replace(":", "").replace("-", "").upper()[:6]
    
    fabricantes = {
        # Google
        "3C5AB4": "Google",
        "001A11": "Google",
        "38EC0D": "Google",
        "F8D0BD": "Google",
        # Apple
        "0016CB": "Apple", "F0B429": "Apple", "D4DC8D": "Apple",
        "98D6BB": "Apple", "A4D1D2": "Apple", "38C986": "Apple",
        "8C8590": "Apple", "B065BD": "Apple", "DC2B61": "Apple",
        "F0D1A9": "Apple", "ACCF5C": "Apple", "68D93C": "Apple",
        # Samsung
        "F0D5BF": "Samsung", "8C3A6D": "Samsung", "CC05E8": "Samsung",
        "78BDBC": "Samsung", "E0D0D0": "Samsung", "F49F54": "Samsung",
        "1814EC": "Samsung", "84C2E4": "Samsung",
        # TP-Link
        "18A6F7": "TP-Link", "50C7BF": "TP-Link", "F4F26D": "TP-Link",
        "14CC20": "TP-Link", "E8DE27": "TP-Link", "F8D111": "TP-Link",
        "A42B8C": "TP-Link", "10FEE0": "TP-Link",
        # Xiaomi
        "D85D4C": "Xiaomi", "64A5C3": "Xiaomi", "8C8CD2": "Xiaomi",
        "F0B429": "Xiaomi", "A4A6A9": "Xiaomi",
        # Huawei
        "F832E4": "Huawei", "28DB81": "Huawei", "48DBFB": "Huawei",
        "6C4B7F": "Huawei", "A40F85": "Huawei",
        # Sony
        "A4A930": "Sony", "1CBA8C": "Sony", "00014A": "Sony",
        "080046": "Sony", "0024BE": "Sony (PlayStation)",
        # Microsoft/Xbox
        "00025B": "Microsoft (Xbox)", "002345": "Microsoft (Xbox)",
        "28E14C": "Microsoft (Xbox)", "001DD8": "Microsoft",
        # Nintendo
        "0013F7": "Nintendo", "0009BF": "Nintendo", "002709": "Nintendo",
        "7CBB8A": "Nintendo", "E8B4C8": "Nintendo Switch",
        # Intel
        "0024D7": "Intel", "0026C6": "Intel", "4C3488": "Intel",
        "001500": "Intel", "0C8BFD": "Intel",
        # HP
        "0001E6": "HP", "3CD92B": "HP", "B4B686": "HP",
        "0060B0": "HP", "001871": "HP",
        # Dell
        "0014A4": "Dell", "002170": "Dell", "F04BCE": "Dell",
        "B84D43": "Dell", "0019B9": "Dell",
        # Lenovo
        "001D72": "Lenovo", "0024CD": "Lenovo", "08EDED": "Lenovo",
        "28D1CB": "Lenovo", "0023B1": "Lenovo",
        # ASUS
        "0017C4": "ASUS", "38D547": "ASUS", "AC9E17": "ASUS",
        "E0CB4E": "ASUS", "08BFB8": "ASUS",
        # LG
        "DC0B34": "LG", "A8A648": "LG", "0022B0": "LG Electronics",
        "F88A3C": "LG", "043EAC": "LG",
        # D-Link
        "000D88": "D-Link", "C8D3A3": "D-Link", "001D7E": "D-Link",
        "1C7EE5": "D-Link", "B0C554": "D-Link",
        # Tenda
        "3498B5": "Tenda", "C83A35": "Tenda", "50D4F7": "Tenda",
        "4C09D4": "Tenda", "B078BA": "Tenda",
        # Cisco
        "0018F8": "Cisco", "0023AC": "Cisco", "F8B156": "Cisco",
        "001AA1": "Cisco", "D48C15": "Cisco",
        # Otros
        "00E04C": "Realtek", "00045A": "Linksys", "F0761C": "ZTE",
        "0013E0": "ZTE", "80EE73": "Philips", "001788": "Philips",
        "001F1F": "Edimax", "000E08": "Ubiquiti",
        "00156D": "Ubiquiti", "0023CD": "Brother (Impresora)",
        "001BA9": "Brother (Impresora)", "0030C1": "Epson (Impresora)",
        "0000DE": "Xerox (Impresora)", "00213C": "Xerox (Impresora)",
        "001109": "Roku", "0025F3": "Roku", "0014D4": "Fitbit",
        "0018B4": "Garmin", "000D18": "Logitech", "046D8F": "Logitech",
        "001E8C": "Motorola", "0026BA": "Motorola",
        "0023EB": "Nokia", "001A8B": "Nokia",
        "001BC5": "HTC", "001E2A": "HTC",
        "0021FB": "OnePlus", "001E3D": "OnePlus",
        "00242C": "Oppo", "001F3B": "Oppo",
        "0025B5": "Vivo", "0023F8": "Vivo",
    }
    
    return fabricantes.get(oui, "No identificado")

def detectar_sistema_operativo(ip, mac, puertos):
    """Detecta el SO por TTL + MAC + puertos"""
    try:
        if platform.system() == "Windows":
            comando = f"ping -n 1 {ip}"
        else:
            comando = f"ping -c 1 {ip}"
        
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        ttl = None
        tiempo = "N/A"
        
        # Buscar TTL y tiempo
        if "TTL=" in resultado.stdout:
            ttl_match = re.search(r"TTL=(\d+)", resultado.stdout)
            if ttl_match:
                ttl = int(ttl_match.group(1))
        
        if "tiempo=" in resultado.stdout.lower() or "time=" in resultado.stdout.lower():
            tiempo_match = re.search(r"(?:tiempo|time)[=<](\d+)", resultado.stdout.lower())
            if tiempo_match:
                tiempo = f"{tiempo_match.group(1)}ms"
        
        if ttl is None:
            return "No detectado", tiempo
        
        # Clasificar por TTL
        if ttl >= 250:
            return "Router/Network Device", tiempo
        elif ttl <= 64:
            # Afinar por MAC y puertos
            if mac and mac != "No disponible":
                oui = mac.replace(":", "").replace("-", "").upper()[:6]
                
                android_fabricantes = [
                    "F0D5BF", "8C3A6D", "CC05E8", "78BDBC", "E0D0D0", "F49F54",
                    "D85D4C", "64A5C3", "8C8CD2", "A4A6A9",
                    "F832E4", "28DB81", "48DBFB", "6C4B7F",
                    "F0761C", "0013E0", "001E8C", "0026BA",
                    "001BC5", "001E2A", "0021FB", "001E3D", "00242C", "0025B5"
                ]
                
                apple_fabricantes = [
                    "0016CB", "F0B429", "D4DC8D", "98D6BB", "A4D1D2",
                    "38C986", "8C8590", "B065BD", "DC2B61", "F0D1A9"
                ]
                
                if oui in android_fabricantes:
                    return "Android", tiempo
                elif oui in apple_fabricantes:
                    return "iOS", tiempo
            
            # Por puertos
            if 5555 in puertos:
                return "Android (ADB)", tiempo
            elif 22 in puertos:
                return "Linux (SSH)", tiempo
            elif 5900 in puertos:
                return "Linux/Unix (VNC)", tiempo
            else:
                return "Linux/Unix", tiempo
        
        elif ttl <= 128:
            # Windows o algunos routers
            if 3389 in puertos:
                return "Windows (RDP)", tiempo
            elif 445 in puertos:
                return "Windows (SMB)", tiempo
            else:
                return "Windows", tiempo
        
        return f"Desconocido (TTL={ttl})", tiempo
    
    except:
        return "Error al detectar", "N/A"

def escanear_puertos(ip):
    """Escanea 100 puertos más comunes"""
    puertos_comunes = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
        548, 554, 587, 631, 853, 993, 995, 1025, 1433, 1521, 1723,
        1900, 2049, 2082, 2083, 2181, 2222, 2375, 2376, 2483, 2484,
        3000, 3128, 3260, 3306, 3389, 3478, 4000, 4100, 4369, 5000,
        5040, 5222, 5353, 5432, 5555, 5601, 5672, 5800, 5900, 5984,
        6000, 6379, 6443, 7000, 7077, 7474, 8000, 8008, 8042, 8080,
        8088, 8090, 8123, 8181, 8443, 8888, 8983, 9000, 9090, 9092,
        9100, 9150, 9200, 9300, 9418, 9443, 9800, 9999, 10000, 15672,
        27017, 27018, 27019, 28015, 28017, 50000, 50030, 50070, 61613, 61616
    ]
    
    puertos_abiertos = []
    
    for puerto in puertos_comunes:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            resultado = sock.connect_ex((ip, puerto))
            if resultado == 0:
                # Nombre del servicio común
                servicios = {
                    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
                    53: "DNS", 80: "HTTP", 443: "HTTPS", 445: "SMB",
                    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
                    5555: "ADB", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
                    8443: "HTTPS-Alt", 27017: "MongoDB", 9200: "Elasticsearch"
                }
                servicio = servicios.get(puerto, "")
                if servicio:
                    puertos_abiertos.append(f"{puerto}({servicio})")
                else:
                    puertos_abiertos.append(str(puerto))
            sock.close()
        except:
            pass
    
    return puertos_abiertos

def obtener_nombre_dispositivo(ip):
    """Intenta obtener el nombre NetBIOS del dispositivo"""
    try:
        nombre = socket.gethostbyaddr(ip)
        return nombre[0]
    except:
        return "N/A"

def clasificar_dispositivo(so, mac, puertos, fabricante):
    """Clasifica el tipo de dispositivo"""
    if "Router" in so:
        return "Router/Gateway"
    if "TV" in fabricante or "Roku" in fabricante or "Philips" in fabricante:
        return "Smart TV / Media"
    if "Impresora" in fabricante or "Brother" in fabricante or "Epson" in fabricante:
        return "Impresora"
    if "Android" in so or "iOS" in so:
        return "Teléfono Móvil"
    if "Windows" in so or "Linux" in so or "macOS" in so:
        return "Computadora"
    if "PlayStation" in fabricante or "Xbox" in fabricante or "Nintendo" in fabricante:
        return "Consola de Videojuegos"
    if "Google" in fabricante:
        return "Altavoz/Asistente"
    if "Fitbit" in fabricante or "Garmin" in fabricante:
        return "Wearable"
    return "Desconocido"

def main():
    print("=" * 70)
    print("   ESCÁNER DE RED LOCAL - VERSIÓN FINAL")
    print("   Detección completa de dispositivos")
    print("=" * 70)
    print("")
    print("Este script escanea tu red local y detecta:")
    print("  - Todos los dispositivos conectados")
    print("  - Dirección IP y MAC")
    print("  - Fabricante del dispositivo")
    print("  - Sistema Operativo (Windows/Linux/Android/iOS/Router)")
    print("  - Puertos abiertos (100 más comunes)")
    print("  - Nombre del dispositivo")
    print("  - Tipo de dispositivo (Móvil, PC, TV, Impresora...)")
    print("  - Tiempo de respuesta (latencia)")
    print("")
    print("=" * 70)
    print("")
    
    ip_base = input("Pon la IP de tu router (ej: 192.168.1.1): ")
    
    partes = ip_base.split(".")
    rango = partes[0] + "." + partes[1] + "." + partes[2]
    
    print("")
    print(f"[*] Escaneando la red {rango}.0/24...")
    print("[*] Esto puede tardar 3-5 minutos. Sé paciente.")
    print("")
    
    dispositivos = []
    inicio_escaneo = time.time()
    
    for i in range(1, 255):
        ip = rango + "." + str(i)
        
        # Ping doble
        encontrado = False
        for intento in range(2):
            if platform.system() == "Windows":
                comando = f"ping -n 1 -w 100 {ip} > nul"
            else:
                comando = f"ping -c 1 -W 0.2 {ip} > /dev/null 2>&1"
            
            respuesta = os.system(comando)
            if respuesta == 0:
                encontrado = True
                break
        
        if encontrado:
            print(f"[+] Vivo: {ip}")
            
            # MAC
            mac = get_mac_address(ip=ip)
            if mac is None:
                mac = "No disponible"
            
            # Fabricante
            print(f"    Identificando fabricante...")
            fabricante = obtener_fabricante(mac)
            
            # Puertos
            print(f"    Escaneando puertos...")
            puertos = escanear_puertos(ip)
            
            # SO y latencia
            print(f"    Detectando sistema operativo...")
            so, latencia = detectar_sistema_operativo(ip, mac, puertos)
            
            # Nombre
            print(f"    Obteniendo nombre...")
            nombre = obtener_nombre_dispositivo(ip)
            
            # Tipo
            tipo = clasificar_dispositivo(so, mac, puertos, fabricante)
            
            dispositivos.append({
                "ip": ip,
                "mac": mac,
                "fabricante": fabricante,
                "so": so,
                "puertos": puertos,
                "nombre": nombre,
                "tipo": tipo,
                "latencia": latencia
            })
            
            print(f"    ├─ MAC: {mac}")
            print(f"    ├─ Fabricante: {fabricante}")
            print(f"    ├─ Sistema Operativo: {so}")
            print(f"    ├─ Tipo: {tipo}")
            print(f"    ├─ Nombre: {nombre}")
            print(f"    ├─ Latencia: {latencia}")
            if puertos:
                print(f"    └─ Puertos: {', '.join(puertos)}")
            else:
                print(f"    └─ Puertos: Ninguno")
            print("")
    
    tiempo_total = round(time.time() - inicio_escaneo, 2)
    
    print("")
    print("=" * 70)
    print(f"   Escaneo completado en {tiempo_total} segundos")
    print(f"   {len(dispositivos)} dispositivos encontrados")
    print("=" * 70)
    
    if len(dispositivos) == 0:
        print("[!] No se encontró nada.")
        print("[!] Consejo: Ejecuta como administrador para mejores resultados.")
        return
    
    # Mostrar resumen
    print("")
    print("   RESUMEN DE DISPOSITIVOS:")
    print("   " + "-" * 66)
    for i, d in enumerate(dispositivos, 1):
        icono = "📱" if "Móvil" in d['tipo'] else "💻" if "Computadora" in d['tipo'] else "📺" if "TV" in d['tipo'] else "🎮" if "Consola" in d['tipo'] else "🖨️" if "Impresora" in d['tipo'] else "🌐" if "Router" in d['tipo'] else "❓"
        print(f"   {i}. {icono} {d['ip']} - {d['fabricante']} - {d['so']} ({d['tipo']})")
    
    # Guardar informe
    ahora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"escaneo_red_{ahora}.txt"
    
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  INFORME DE ESCANEO DE RED\n")
        f.write(f"  Fecha: {ahora}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Red escaneada: {rango}.0/24\n")
        f.write(f"Tiempo de escaneo: {tiempo_total} segundos\n")
        f.write(f"Dispositivos encontrados: {len(dispositivos)}\n\n")
        
        for i, d in enumerate(dispositivos, 1):
            f.write(f"{'─' * 70}\n")
            f.write(f"  DISPOSITIVO {i}\n")
            f.write(f"{'─' * 70}\n")
            f.write(f"  IP:              {d['ip']}\n")
            f.write(f"  MAC:             {d['mac']}\n")
            f.write(f"  Fabricante:      {d['fabricante']}\n")
            f.write(f"  SO:              {d['so']}\n")
            f.write(f"  Tipo:            {d['tipo']}\n")
            f.write(f"  Nombre:          {d['nombre']}\n")
            f.write(f"  Latencia:        {d['latencia']}\n")
            if d['puertos']:
                f.write(f"  Puertos:         {', '.join(d['puertos'])}\n")
            else:
                f.write(f"  Puertos:         Ninguno\n")
            f.write("\n")
        
if __name__ == "__main__":
    main()
