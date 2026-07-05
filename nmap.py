import socket
import sys
import os
from datetime import datetime

V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"""{C}{B}
╔══════════════════════════════════════════════════╗
║        PORT SCANNER PRO                           ║
║        Nmap-like Scanner in Python                ║
╚══════════════════════════════════════════════════╝{N}
""")

# Base de datos de servicios comunes
SERVICES = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    42: "WINS", 43: "WHOIS", 53: "DNS", 67: "DHCP-SERVER", 68: "DHCP-CLIENT",
    69: "TFTP", 80: "HTTP", 88: "Kerberos", 110: "POP3", 111: "RPC",
    119: "NNTP", 123: "NTP", 135: "MSRPC", 137: "NetBIOS-NS", 138: "NetBIOS-DGM",
    139: "NetBIOS-SSN", 143: "IMAP", 161: "SNMP", 162: "SNMPTRAP", 179: "BGP",
    194: "IRC", 389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    514: "RSH", 515: "LPD", 543: "KLOGIN", 544: "KSHELL", 548: "AFP",
    554: "RTSP", 587: "SMTP", 631: "CUPS", 636: "LDAPS", 873: "RSYNC",
    902: "VMware", 993: "IMAPS", 995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN",
    1433: "MSSQL", 1521: "Oracle", 1701: "L2TP", 1723: "PPTP", 1883: "MQTT",
    2049: "NFS", 2082: "cPanel", 2083: "cPanel-SSL", 2181: "ZooKeeper",
    2222: "SSH-Alt", 2375: "Docker", 2376: "Docker-SSL", 3000: "Grafana",
    3128: "Squid", 3260: "iSCSI", 3306: "MySQL", 3389: "RDP", 3478: "STUN",
    4000: "Diablo-II", 4369: "Erlang", 4444: "Metasploit", 4567: "Verizon",
    5000: "UPnP", 5040: "CDDB", 5060: "SIP", 5061: "SIP-TLS", 5222: "XMPP",
    5353: "mDNS", 5357: "WSDAPI", 5432: "PostgreSQL", 5555: "Android-ADB",
    5601: "Kibana", 5672: "RabbitMQ", 5700: "Camfrog", 5800: "VNC-HTTP",
    5900: "VNC", 5901: "VNC-1", 5938: "TeamViewer", 5984: "CouchDB",
    5985: "WinRM-HTTP", 5986: "WinRM-HTTPS", 6000: "X11", 6379: "Redis",
    6443: "K8s-API", 6667: "IRC", 6969: "BT-Tracker", 7000: "Cassandra",
    7001: "Cassandra-SSL", 7077: "Spark", 7474: "Neo4j", 8000: "HTTP-Alt",
    8008: "HTTP-Alt", 8080: "HTTP-Proxy", 8088: "HTTP-Alt", 8090: "HTTP-Alt",
    8123: "Polipo", 8181: "HTTP-Alt", 8443: "HTTPS-Alt", 8888: "HTTP-Alt",
    8983: "Solr", 9000: "SonarQube", 9001: "Hadoop", 9042: "Cassandra",
    9090: "WebSM", 9092: "Kafka", 9100: "JetDirect", 9200: "Elasticsearch",
    9300: "Elasticsearch", 9418: "Git", 9443: "HTTPS-Alt", 9800: "WebDAV",
    9999: "HTTP-Alt", 10000: "Webmin", 11211: "Memcached", 15672: "RabbitMQ-MGMT",
    27017: "MongoDB", 27018: "MongoDB", 27019: "MongoDB", 28015: "RethinkDB",
    28017: "MongoDB", 50000: "SAP", 50030: "Hadoop", 50070: "Hadoop",
    50090: "Hadoop", 61613: "ActiveMQ", 61616: "ActiveMQ",
}

def get_service(port):
    """Obtiene el nombre del servicio para un puerto"""
    return SERVICES.get(port, "unknown")

def scan_port(host, port, timeout=1):
    """Escanea un puerto específico"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def grab_banner(host, port, timeout=2):
    """Intenta obtener el banner del servicio"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode(errors="ignore").strip()
        sock.close()
        return banner[:100] if banner else ""
    except:
        return ""

def main():
    banner()
    
    target = input(f"{B}IP o dominio a escanear:{N} ").strip()
    
    # Resolver dominio a IP
    try:
        ip = socket.gethostbyname(target)
        if ip != target:
            print(f"\n{V}[+] {target} -> {ip}{N}")
    except:
        print(f"\n{R}[!] No se pudo resolver: {target}{N}")
        return
    
    print(f"\n{B}[*] Opciones de escaneo:{N}")
    print(f"    1. Puertos comunes (Top 100)")
    print(f"    2. Puertos web (80, 443, 8080, 8443, 3000, 5000, 8000, 8888, 9000, 9090)")
    print(f"    3. Puertos de base de datos (3306, 5432, 1433, 27017, 6379, 9200)")
    print(f"    4. Puertos de acceso remoto (22, 23, 3389, 5900, 5800)")
    print(f"    5. Rango personalizado")
    print(f"    6. Todos los puertos (1-65535) - MUY LENTO")
    
    opcion = input(f"\n{B}Elige (1-6, Enter=1):{N} ").strip() or "1"
    
    if opcion == "1":
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                 993, 995, 1433, 1521, 1723, 3306, 3389, 5432, 5900, 5985, 5986,
                 6379, 6443, 8080, 8443, 8888, 9090, 9200, 9300, 11211, 15672,
                 27017, 27018, 27019, 28015, 50000, 50030, 50070]
        ports += [3000, 5000, 7000, 8000, 9000, 10000, 20000, 22222, 44444]
        # Puertos web adicionales
        ports += [81, 82, 83, 84, 85, 88, 800, 808, 888, 900, 909, 1000, 2000]
        ports += [3001, 4000, 4001, 4002, 4040, 4444, 5001, 5050, 5555, 5601]
        ports += [6000, 6001, 6666, 6667, 6969, 7001, 7002, 7070, 7777, 8001]
        ports += [8009, 8081, 8082, 8083, 8089, 8181, 8444, 8880, 8889, 8989]
        ports += [9001, 9002, 9091, 9095, 9201, 9999, 10001, 12345, 31337, 49152]
        ports = sorted(set(ports))
    elif opcion == "2":
        ports = [80, 81, 82, 83, 84, 85, 88, 443, 800, 808, 888, 900, 909,
                 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 8080, 8443,
                 8888, 9000, 9090, 9443, 10000, 20000, 22222, 44444]
    elif opcion == "3":
        ports = [1433, 1521, 3306, 5432, 6379, 9200, 9300, 11211, 27017,
                 27018, 27019, 28015, 50000, 50030, 50070]
    elif opcion == "4":
        ports = [21, 22, 23, 115, 514, 3389, 5800, 5900, 5901, 5902, 5938,
                 5985, 5986, 10000]
    elif opcion == "5":
        try:
            inicio = int(input(f"{B}Puerto inicial:{N} ").strip())
            fin = int(input(f"{B}Puerto final:{N} ").strip())
            ports = list(range(inicio, fin + 1))
        except:
            print(f"{R}[!] Puertos inválidos{N}")
            return
    elif opcion == "6":
        ports = list(range(1, 65536))
        print(f"{A}[!] Esto puede tardar MUCHO tiempo{N}")
    else:
        ports = list(range(1, 1025))
    
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}   ESCANEANDO {target} ({ip}){N}")
    print(f"{C}   Puertos a probar: {len(ports)}{N}")
    print(f"{C}   Hora: {datetime.now().strftime('%H:%M:%S')}{N}")
    print(f"{C}{'='*50}{N}\n")
    
    open_ports = []
    start_time = datetime.now()
    
    for i, port in enumerate(ports, 1):
        if scan_port(ip, port, 0.5):
            service = get_service(port)
            banner = grab_banner(ip, port)
            
            if banner:
                print(f"  {V}[OPEN] {port}/tcp - {service} - {banner}{N}")
            else:
                print(f"  {V}[OPEN] {port}/tcp - {service}{N}")
            
            open_ports.append({
                "port": port,
                "service": service,
                "banner": banner
            })
        
        # Barra de progreso cada 50 puertos
        if i % 50 == 0:
            pct = (i / len(ports)) * 100
            print(f"  {A}[*] Progreso: {i}/{len(ports)} ({pct:.1f}%){N}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Guardar resultados
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo = f"portscan_{target.replace('.', '_')}_{ts}.txt"
    
    with open(archivo, "w") as f:
        f.write(f"Port Scanner Pro\n")
        f.write(f"Objetivo: {target} ({ip})\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duración: {duration:.1f}s\n")
        f.write(f"Puertos escaneados: {len(ports)}\n")
        f.write(f"{'='*50}\n\n")
        
        for p in open_ports:
            f.write(f"[OPEN] {p['port']}/tcp - {p['service']}\n")
            if p['banner']:
                f.write(f"  Banner: {p['banner']}\n")
    
    # Resumen
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}{B}   RESULTADOS{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Total puertos: {len(ports)}")
    print(f"  Puertos abiertos: {V}{len(open_ports)}{N}")
    print(f"  Duración: {duration:.1f} segundos")
    print(f"  Archivo: {archivo}")
    print(f"{C}{'='*50}{N}\n")
    
    if open_ports:
        print(f"{B}Puertos abiertos:{N}")
        for p in open_ports:
            print(f"  {V}{p['port']}/tcp{N} - {p['service']}")
    else:
        print(f"  {A}No se encontraron puertos abiertos.{N}")
    
    os.system("pause")

if __name__ == "__main__":
    main()
