import requests
from datetime import datetime
import os
import re
import json

V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"""{C}{B}
╔══════════════════════════════════════════════════╗
║        EMAIL HARVESTER PRO                        ║
║        OSINT Email Finder                         ║
╚══════════════════════════════════════════════════╝{N}
""")

def hunter_search(dominio):
    """Busca emails usando Hunter.io (sin API key)"""
    emails = []
    try:
        url = f"https://api.hunter.io/v2/domain-search?domain={dominio}&limit=100"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for email in data.get("data", {}).get("emails", []):
                emails.append({
                    "email": email["value"],
                    "type": email.get("type", "personal"),
                    "confidence": email.get("confidence", 0),
                    "sources": len(email.get("sources", [])),
                    "source": "Hunter.io"
                })
    except:
        pass
    return emails

def emailrep_search(dominio):
    """Busca emails usando EmailRep.io"""
    emails = []
    try:
        url = f"https://emailrep.io/{dominio}"
        headers = {"User-Agent": "EmailHarvester/1.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for email in data.get("emails", []):
                emails.append({
                    "email": email,
                    "type": "personal",
                    "confidence": 50,
                    "sources": 1,
                    "source": "EmailRep.io"
                })
    except:
        pass
    return emails

def github_search(dominio):
    """Busca emails en GitHub"""
    emails = []
    try:
        url = f"https://api.github.com/search/code?q={dominio}+email"
        headers = {"Accept": "application/vnd.github.v3+json"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("items", [])[:10]:
                # Buscar emails en el contenido
                html_url = item.get("html_url", "")
                if html_url:
                    raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                    try:
                        raw_r = requests.get(raw_url, timeout=5)
                        found = re.findall(r'[a-zA-Z0-9._%+-]+@' + re.escape(dominio), raw_r.text)
                        for email in found:
                            if email not in [e["email"] for e in emails]:
                                emails.append({
                                    "email": email,
                                    "type": "personal",
                                    "confidence": 70,
                                    "sources": 1,
                                    "source": "GitHub"
                                })
                    except:
                        pass
    except:
        pass
    return emails

def google_search(dominio):
    """Busca emails vía Google ( scraping básico)"""
    emails = []
    try:
        # Usamos una API pública de búsqueda
        url = f"https://www.google.com/search?q=%40{dominio}+email"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            found = re.findall(r'[a-zA-Z0-9._%+-]+@' + re.escape(dominio), r.text)
            for email in found[:20]:
                if email not in [e["email"] for e in emails]:
                    emails.append({
                        "email": email,
                        "type": "personal",
                        "confidence": 30,
                        "sources": 1,
                        "source": "Google"
                    })
    except:
        pass
    return emails

def check_patterns(dominio):
    """Genera patrones comunes de emails corporativos"""
    patterns = []
    nombres = [
        "info", "admin", "contact", "support", "sales", "hello",
        "security", "abuse", "webmaster", "postmaster", "hostmaster",
        "marketing", "press", "media", "jobs", "careers", "hr",
        "legal", "privacy", "gdpr", "dpo", "dev", "ops", "noc",
        "billing", "finance", "accounts", "office", "help", "root",
        "administrator", "guest", "test", "demo", "user",
    ]
    
    for nombre in nombres:
        patterns.append({
            "email": f"{nombre}@{dominio}",
            "type": "role-based",
            "confidence": 10,
            "sources": 0,
            "source": "Pattern"
        })
    
    return patterns

def check_mx(dominio):
    """Verifica si el dominio tiene servidor de correo"""
    import socket
    try:
        records = socket.gethostbyname_ex(f"mail.{dominio}")
        if records:
            return True, "mail." + dominio
    except:
        pass
    
    try:
        records = socket.gethostbyname_ex(dominio)
        if records:
            return True, dominio
    except:
        pass
    
    return False, ""

def main():
    banner()
    
    dominio = input(f"{B}Dominio (ej: empresa.com):{N} ").strip().lower()
    
    if not dominio or "." not in dominio:
        print(f"{R}[!] Dominio inválido{N}")
        return
    
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}   BUSCANDO EMAILS DE {dominio.upper()}{N}")
    print(f"{C}{'='*50}{N}")
    
    # Verificar MX
    print(f"\n{B}[*] Verificando servidor de correo...{N}")
    tiene_mx, mx_server = check_mx(dominio)
    if tiene_mx:
        print(f"  {V}[+] Servidor MX: {mx_server}{N}")
    else:
        print(f"  {A}[!] No se detectó servidor MX{N}")
    
    all_emails = []
    
    # Hunter.io
    print(f"\n{B}[*] Buscando en Hunter.io...{N}")
    emails = hunter_search(dominio)
    if emails:
        for e in emails:
            print(f"  {V}[Hunter] {e['email']} ({e['type']}, {e['confidence']}%){N}")
            all_emails.append(e)
    else:
        print(f"  {A}Sin resultados{N}")
    
    # EmailRep.io
    print(f"\n{B}[*] Buscando en EmailRep.io...{N}")
    emails = emailrep_search(dominio)
    if emails:
        for e in emails:
            print(f"  {V}[EmailRep] {e['email']}{N}")
            all_emails.append(e)
    else:
        print(f"  {A}Sin resultados{N}")
    
    # GitHub
    print(f"\n{B}[*] Buscando en GitHub...{N}")
    emails = github_search(dominio)
    if emails:
        for e in emails:
            print(f"  {V}[GitHub] {e['email']}{N}")
            all_emails.append(e)
    else:
        print(f"  {A}Sin resultados (o límite de API){N}")
    
    # Google
    print(f"\n{B}[*] Buscando en Google...{N}")
    emails = google_search(dominio)
    if emails:
        for e in emails:
            print(f"  {V}[Google] {e['email']}{N}")
            all_emails.append(e)
    else:
        print(f"  {A}Sin resultados{N}")
    
    # Patrones
    print(f"\n{B}[*] Añadiendo patrones comunes...{N}")
    patterns = check_patterns(dominio)
    for p in patterns[:10]:
        all_emails.append(p)
    print(f"  {V}[+] {len(patterns)} patrones generados{N}")
    
    # Eliminar duplicados
    unique = {}
    for e in all_emails:
        if e["email"] not in unique:
            unique[e["email"]] = e
    
    all_emails = list(unique.values())
    
    # Guardar resultados
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_txt = f"emails_{dominio.replace('.', '_')}_{ts}.txt"
    archivo_json = f"emails_{dominio.replace('.', '_')}_{ts}.json"
    
    with open(archivo_txt, "w") as f:
        f.write(f"Email Harvester Pro\n")
        f.write(f"Dominio: {dominio}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(all_emails)} emails\n")
        f.write(f"{'='*50}\n\n")
        
        f.write("CONFIRMADOS (fuentes externas):\n")
        f.write("-" * 30 + "\n")
        for e in all_emails:
            if e["sources"] > 0:
                f.write(f"  {e['email']} - {e['source']} ({e['type']})\n")
        
        f.write("\nPATRONES (no verificados):\n")
        f.write("-" * 30 + "\n")
        for e in all_emails:
            if e["sources"] == 0:
                f.write(f"  {e['email']} - Pattern ({e['type']})\n")
    
    with open(archivo_json, "w") as f:
        json.dump(all_emails, f, indent=2)
    
    # Resumen
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}{B}   RESULTADOS FINALES{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Total emails: {V}{len(all_emails)}{N}")
    print(f"  Confirmados: {V}{len([e for e in all_emails if e['sources'] > 0])}{N}")
    print(f"  Patrones: {V}{len([e for e in all_emails if e['sources'] == 0])}{N}")
    print(f"  Archivos: {archivo_txt}, {archivo_json}")
    print(f"{C}{'='*50}{N}\n")
    
    # Mostrar mejores resultados
    print(f"{B}Mejores emails:{N}")
    for e in all_emails[:20]:
        if e["sources"] > 0:
            print(f"  {V}[{e['source']}] {e['email']} ({e['confidence']}%){N}")
        else:
            print(f"  {A}[?] {e['email']}{N}")
    
    os.system("pause")

if __name__ == "__main__":
    main()
