import requests
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"""{C}{B}
╔══════════════════════════════════════════════════╗
║        FILE FINDER PRO v2.0                       ║
║        Advanced File Discovery Tool               ║
╚══════════════════════════════════════════════════╝{N}
""")

def cargar_wordlist():
    """Wordlist de 200+ nombres comunes de archivos y directorios"""
    return [
        # ===== CONFIGURACIÓN =====
        "config", "configuration", "settings", "setup", "install",
        "database", "db", "mysql", "sql", "wp-config",
        ".env", ".gitignore", ".htaccess", ".htpasswd",
        "robots", "sitemap", "crossdomain",
        "appsettings", "web.config", "package.json", "composer.json",
        "docker-compose", "docker-compose.yml", "Dockerfile",
        "Makefile", "Gemfile", "Rakefile", "Procfile",
        "application", "bootstrap", "autoload",
        "security", "firewall", "proxy",
        
        # ===== BACKUPS =====
        "backup", "backups", "old", "copy", "dump", "export",
        "www", "wwwroot", "htdocs", "public_html",
        "backup_db", "backup_site", "backup_www",
        "site_backup", "db_backup", "full_backup",
        "archive", "archives", "snapshot",
        "copy_of", "old_site", "old_version",
        "v1", "v2", "v3", "beta", "alpha", "dev", "staging",
        "production", "development", "testing",
        
        # ===== INFORMACIÓN =====
        "readme", "changelog", "license", "version", "info",
        "phpinfo", "test", "debug", "log", "logs",
        "error", "errors", "trace", "status",
        "about", "credits", "authors", "contributors",
        "history", "release", "releases", "news",
        "todo", "tasks", "issues", "bugs",
        
        # ===== USUARIOS Y CONTRASEÑAS =====
        "users", "user", "accounts", "account", "passwords", "password",
        "pass", "credenciales", "credentials", "secret", "secrets",
        "admin", "administrator", "root",
        "passwd", "shadow", "group",
        "userlist", "user_list", "members", "clients",
        "auth", "authentication", "login", "register", "signup",
        "forgot", "reset", "recovery",
        
        # ===== ARCHIVOS COMUNES =====
        "index", "main", "home", "default", "page",
        "header", "footer", "sidebar", "menu", "nav",
        "style", "styles", "script", "scripts", "app",
        "api", "rest", "graphql", "swagger", "openapi",
        "package", "composer", "docker", "makefile", "gemfile",
        "manifest", "bower", "npm", "yarn", "gulp", "grunt",
        "webpack", "vite", "rollup", "esbuild",
        
        # ===== ARCHIVOS DE SISTEMA =====
        "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
        "authorized_keys", "known_hosts",
        "shadow", "passwd", "group", "hosts", "resolv",
        "cron", "crontab", "bashrc", "bash_profile", "profile",
        "zshrc", "fish_config", "init", "systemd",
        "sudoers", "fstab", "mtab", "exports",
        "syslog", "messages", "auth.log", "access.log",
        
        # ===== WEB =====
        "upload", "uploads", "download", "downloads", "files",
        "images", "img", "css", "js", "assets", "static",
        "includes", "inc", "lib", "vendor", "node_modules",
        "public", "resources", "storage", "dist", "build",
        "media", "videos", "audio", "docs", "documents",
        "tmp", "temp", "cache", "sessions", "data",
        
        # ===== CMS =====
        "wordpress", "joomla", "drupal", "magento",
        "wp-login", "wp-admin", "xmlrpc",
        "wp-content", "wp-includes", "wp-json",
        "typo3", "prestashop", "shopify", "woocommerce",
        "craft", "ghost", "hugo", "jekyll", "gatsby", "next",
        
        # ===== EMAIL =====
        "mail", "email", "smtp", "pop3", "imap",
        "webmail", "roundcube", "squirrelmail",
        "phpmailer", "sendmail", "postfix", "exim",
        "newsletter", "subscribe", "unsubscribe",
        
        # ===== OTROS =====
        "security", "privacy", "terms", "policy", "cookies",
        "gdpr", "legal", "disclaimer", "trademark",
        "contact", "about", "faq", "help", "support",
        "docs", "documentation", "wiki", "manual", "guide",
        "tutorial", "examples", "samples", "demo",
        "api-docs", "developer", "developers", "devportal",
        "status", "health", "ping", "monitor", "uptime",
        "metrics", "stats", "statistics", "analytics",
    ]

def extensiones_por_categoria(categoria):
    """Devuelve extensiones según categoría"""
    categorias = {
        "config": ["php", "ini", "conf", "cfg", "env", "json", "xml", "yml", "yaml", "toml", "properties", "cnf"],
        "backup": ["sql", "zip", "tar", "gz", "bz2", "bak", "old", "dump", "rar", "7z", "tgz", "sql.gz", "backup"],
        "docs": ["txt", "md", "pdf", "doc", "docx", "xls", "xlsx", "csv", "log", "rtf", "odt", "ppt", "pptx"],
        "source": ["py", "js", "java", "cpp", "h", "rb", "go", "rs", "ts", "jsx", "tsx", "vue", "svelte", "php", "asp", "aspx", "jsp", "cgi", "pl", "sh", "bash", "zsh", "fish", "ps1", "bat", "cmd"],
        "data": ["json", "xml", "csv", "tsv", "yaml", "yml", "sqlite", "db", "sqlite3", "mdb", "accdb"],
        "image": ["jpg", "jpeg", "png", "gif", "svg", "ico", "bmp", "webp", "tiff", "psd", "ai", "eps"],
        "cert": ["pem", "crt", "key", "cer", "der", "p12", "pfx", "p7b", "csr"],
        "log": ["log", "txt", "out", "err", "debug", "trace"],
    }
    return categorias.get(categoria, [])

def probar_url(url, encontrados, lock, stats):
    """Prueba una URL individual"""
    try:
        r = requests.head(url, timeout=3, allow_redirects=False)
        if r.status_code == 200:
            size = r.headers.get("Content-Length", "?")
            with lock:
                print(f"  {V}[FOUND] {url} ({size} bytes){N}")
                encontrados.append({"url": url, "size": size, "status": 200})
        elif r.status_code == 403:
            with lock:
                print(f"  {A}[403] {url}{N}")
                encontrados.append({"url": url, "size": "403", "status": 403})
        elif r.status_code == 401:
            with lock:
                print(f"  {A}[401] {url}{N}")
                encontrados.append({"url": url, "size": "401", "status": 401})
        elif r.status_code == 500:
            with lock:
                print(f"  {R}[500] {url}{N}")
                encontrados.append({"url": url, "size": "500", "status": 500})
    except:
        pass
    
    with lock:
        stats["probados"] += 1
        if stats["probados"] % 25 == 0:
            pct = (stats["probados"] / stats["total"]) * 100
            print(f"  {A}[*] {stats['probados']}/{stats['total']} ({pct:.1f}%) - Encontrados: {len(encontrados)}{N}")

def buscar_archivos_multihilo(url_base, wordlist, extensiones, hilos=10):
    """Busca archivos usando múltiples hilos"""
    encontrados = []
    urls = []
    
    for nombre in wordlist:
        for ext in extensiones:
            urls.append(f"{url_base}/{nombre}.{ext}")
    
    lock = threading.Lock()
    stats = {"probados": 0, "total": len(urls)}
    
    print(f"\n{B}[*] Iniciando búsqueda con {hilos} hilos...{N}")
    print(f"{B}[*] URLs a probar: {len(urls)}{N}\n")
    
    with ThreadPoolExecutor(max_workers=hilos) as executor:
        futures = {executor.submit(probar_url, url, encontrados, lock, stats): url for url in urls}
        
        for future in as_completed(futures):
            pass
    
    return encontrados, stats["probados"]

def buscar_directorios(url_base, wordlist, hilos=10):
    """Busca directorios comunes"""
    encontrados = []
    urls = [f"{url_base}/{nombre}/" for nombre in wordlist]
    
    lock = threading.Lock()
    stats = {"probados": 0, "total": len(urls)}
    
    print(f"\n{B}[*] Buscando directorios ({len(urls)} URLs)...{N}\n")
    
    with ThreadPoolExecutor(max_workers=hilos) as executor:
        futures = {executor.submit(probar_url, url, encontrados, lock, stats): url for url in urls}
        for future in as_completed(futures):
            pass
    
    return encontrados

def main():
    banner()
    
    url = input(f"{B}URL base (ej: https://ejemplo.com):{N} ").strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url
    
    print(f"\n{B}[*] Modo de búsqueda:{N}")
    print(f"    1. Archivos de configuración (php, ini, env, json, xml, yml...)")
    print(f"    2. Backups y bases de datos (sql, zip, tar, gz, bak, dump...)")
    print(f"    3. Documentos (txt, md, pdf, doc, csv, log...)")
    print(f"    4. Código fuente (py, js, java, cpp, rb, go, php...)")
    print(f"    5. Datos (json, xml, csv, sqlite, db...)")
    print(f"    6. Imágenes (jpg, png, gif, svg, ico...)")
    print(f"    7. Certificados (pem, crt, key, cer, p12...)")
    print(f"    8. Logs (log, txt, out, err, debug...)")
    print(f"    9. Personalizado (tú eliges las extensiones)")
    print(f"   10. TODAS las categorías")
    print(f"   11. Buscar solo DIRECTORIOS (sin extensiones)")
    
    opcion = input(f"\n{B}Elige (1-11, Enter=1):{N} ").strip() or "1"
    
    categorias_map = {
        "1": "config", "2": "backup", "3": "docs", "4": "source",
        "5": "data", "6": "image", "7": "cert", "8": "log"
    }
    
    if opcion in categorias_map:
        extensiones = extensiones_por_categoria(categorias_map[opcion])
    elif opcion == "9":
        ext_input = input(f"{B}Extensiones (separadas por coma, ej: txt,php,zip):{N} ").strip()
        extensiones = [e.strip() for e in ext_input.split(",") if e.strip()]
    elif opcion == "10":
        extensiones = []
        for cat in ["config", "backup", "docs", "source", "data", "log"]:
            extensiones.extend(extensiones_por_categoria(cat))
        extensiones = list(set(extensiones))
    elif opcion == "11":
        extensiones = None
    else:
        extensiones = extensiones_por_categoria("config")
    
    wordlist = cargar_wordlist()
    
    # Configurar hilos
    try:
        hilos = int(input(f"{B}Hilos (1-50, Enter=10):{N} ") or "10")
        hilos = max(1, min(50, hilos))
    except:
        hilos = 10
    
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}   FILE FINDER PRO v2.0{N}")
    print(f"{C}   URL: {url}{N}")
    if extensiones:
        print(f"{C}   Extensiones: {', '.join(extensiones[:10])}{'...' if len(extensiones) > 10 else ''}{N}")
        print(f"{C}   Combinaciones: {len(wordlist) * len(extensiones)}{N}")
    else:
        print(f"{C}   Directorios: {len(wordlist)}{N}")
    print(f"{C}   Hilos: {hilos}{N}")
    print(f"{C}{'='*50}{N}")
    
    encontrados = []
    probados = 0
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo = f"files_{url.replace('://', '_').replace('/', '_')[:40]}_{ts}.txt"
    
    with open(archivo, "w") as f:
        f.write(f"File Finder Pro v2.0\n")
        f.write(f"URL: {url}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if extensiones:
            f.write(f"Extensions: {', '.join(extensiones)}\n")
        else:
            f.write(f"Mode: Directories only\n")
        f.write(f"Words: {len(wordlist)}\n")
        f.write(f"Threads: {hilos}\n")
        f.write(f"{'='*50}\n\n")
        
        if extensiones:
            encontrados, probados = buscar_archivos_multihilo(url, wordlist, extensiones, hilos)
        else:
            encontrados = buscar_directorios(url, wordlist, hilos)
            probados = len(wordlist)
        
        f.write(f"\n{'='*50}\n")
        f.write(f"Total found: {len(encontrados)}\n")
        f.write(f"Total tested: {probados}\n")
        
        # Categorizar resultados
        f.write(f"\n--- BY STATUS ---\n")
        status_200 = [e for e in encontrados if e.get("status") == 200]
        status_403 = [e for e in encontrados if e.get("status") == 403]
        status_401 = [e for e in encontrados if e.get("status") == 401]
        status_500 = [e for e in encontrados if e.get("status") == 500]
        
        f.write(f"200 OK: {len(status_200)}\n")
        f.write(f"403 Forbidden: {len(status_403)}\n")
        f.write(f"401 Unauthorized: {len(status_401)}\n")
        f.write(f"500 Error: {len(status_500)}\n")
        
        for e in status_200:
            f.write(f"  [200] {e['url']} ({e['size']} bytes)\n")
        for e in status_403:
            f.write(f"  [403] {e['url']}\n")
        for e in status_401:
            f.write(f"  [401] {e['url']}\n")
        for e in status_500:
            f.write(f"  [500] {e['url']}\n")
    
    print(f"\n{C}{'='*50}{N}")
    print(f"{C}{B}   FILE FINDER DONE{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Probados: {probados}")
    print(f"  200 OK: {V}{len([e for e in encontrados if e.get('status') == 200])}{N}")
    print(f"  403: {A}{len([e for e in encontrados if e.get('status') == 403])}{N}")
    print(f"  401: {A}{len([e for e in encontrados if e.get('status') == 401])}{N}")
    print(f"  500: {R}{len([e for e in encontrados if e.get('status') == 500])}{N}")
    print(f"  Archivo: {archivo}")
    print(f"{C}{'='*50}{N}\n")
    
    encontrados_200 = [e for e in encontrados if e.get("status") == 200]
    if encontrados_200:
        print(f"{B}Archivos encontrados (200 OK):{N}")
        for e in encontrados_200[:30]:
            print(f"  {V}[{e['size']}]{N} {e['url']}")
    
    encontrados_403 = [e for e in encontrados if e.get("status") == 403]
    if encontrados_403 and len(encontrados_403) <= 10:
        print(f"\n{B}Acceso restringido (403):{N}")
        for e in encontrados_403:
            print(f"  {A}[-]{N} {e['url']}")
    
    os.system("pause")

if __name__ == "__main__":
    main()
