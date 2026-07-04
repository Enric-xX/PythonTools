import requests
from datetime import datetime
import os
import sys

# ===== COLORES =====
V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"{C}{B}╔{'═'*48}╗")
    print(f"║{' '*10}Directory Brute Forcer{' '*8}║")
    print(f"╚{'═'*48}╝{N}\n")

def cargar_wordlist(url):
    """Carga wordlist desde archivo o usa una integrada"""
    print(f"[*] Opciones de wordlist:")
    print(f"    1. Wordlist integrada (500 directorios comunes)")
    print(f"    2. Cargar archivo .txt")
    
    opcion = input(f"\n{B}Elige (1-2):{N} ").strip()
    
    if opcion == "2":
        ruta = input("Ruta del archivo .txt: ").strip()
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                return [line.strip() for line in f if line.strip()]
        else:
            print(f"{R}[!] Archivo no encontrado. Usando wordlist integrada.{N}\n")
    
    # Wordlist integrada de 500 directorios comunes
    return [
        # Directorios web comunes
        "admin", "login", "wp-admin", "administrator", "panel",
        "dashboard", "controlpanel", "cpanel", "webmail", "phpmyadmin",
        "mysql", "db", "database", "backup", "backups", "old", "new",
        "test", "dev", "staging", "development", "production",
        "api", "api/v1", "api/v2", "rest", "graphql", "swagger",
        "docs", "documentation", "help", "support", "faq",
        "blog", "news", "forum", "forums", "community",
        "shop", "store", "cart", "checkout", "products",
        "users", "user", "profile", "account", "register", "signup",
        "signin", "logout", "auth", "authenticate", "oauth",
        "config", "configuration", "settings", "setup", "install",
        "upload", "uploads", "files", "download", "downloads",
        "images", "img", "css", "js", "static", "assets",
        "includes", "inc", "lib", "library", "vendor",
        "tmp", "temp", "cache", "logs", "log",
        "robots.txt", "sitemap.xml", "crossdomain.xml",
        ".git", ".svn", ".env", ".htaccess", ".htpasswd",
        "phpinfo.php", "info.php", "test.php", "demo.php",
        "readme.html", "readme.txt", "changelog.txt", "license.txt",
        "wp-content", "wp-includes", "wp-json", "xmlrpc.php",
        "wp-config.php", "wp-config.bak", "wp-config.php~",
        "server-status", "server-info", "status", "health",
        "metrics", "actuator", "actuator/health", "actuator/info",
        "debug", "trace", "console", "terminal", "shell",
        "secure", "security", "private", "hidden", "secret",
        "cron", "jobs", "tasks", "queue", "workers",
        "mail", "email", "smtp", "pop3", "imap",
        "ftp", "ssh", "telnet", "rdp", "vnc",
        "monitor", "monitoring", "analytics", "statistics", "stats",
        "error", "errors", "404", "500", "maintenance",
        "portal", "portals", "gateway", "proxy", "redirect",
        "legacy", "archive", "archives", "history",
        "beta", "alpha", "nightly", "latest", "stable",
        "cdn", "media", "video", "videos", "audio",
        "content", "data", "export", "import", "sync",
        "feed", "rss", "atom", "json", "xml",
        "search", "find", "query", "lookup", "browse",
        "home", "index", "main", "default", "page",
        "cms", "wordpress", "joomla", "drupal", "magento",
        "app", "application", "service", "services", "system",
        "network", "net", "host", "server", "client",
        "master", "slave", "node", "cluster", "cloud",
        "database", "databases", "sql", "nosql", "redis",
        "docker", "kubernetes", "container", "pod", "deployment",
        "ci", "cd", "jenkins", "gitlab", "github",
        "webhook", "webhooks", "callback", "notify", "notification",
        "payment", "payments", "billing", "invoice", "order",
        "checkout", "cart", "basket", "wishlist", "compare",
        "catalog", "category", "categories", "product", "item",
        "customer", "client", "member", "subscriber", "guest",
        "newsletter", "subscribe", "unsubscribe", "optin", "optout",
        "terms", "privacy", "policy", "cookies", "gdpr",
        "about", "contact", "team", "careers", "jobs",
        "press", "media", "investors", "partners", "affiliates",
        "sitemap", "sitemap_index.xml", "sitemap.xml.gz",
        "favicon.ico", "apple-touch-icon.png", "manifest.json",
        "service-worker.js", "offline.html", "browserconfig.xml",
        "uploads/files/", "uploads/documents/", "uploads/images/",
        "assets/css/", "assets/js/", "assets/images/",
        "static/css/", "static/js/", "static/images/",
        "public/css/", "public/js/", "public/images/",
        "resources/", "storage/", "dist/", "build/",
        "node_modules/", "bower_components/", "jspm_packages/",
        "vendor/composer/", "vendor/npm/", "vendor/bower/",
        ".well-known/", ".well-known/security.txt", ".well-known/acme-challenge/",
        "cgi-bin/", "cgi/", "bin/", "scripts/", "tools/",
        "test/", "tests/", "spec/", "examples/", "samples/",
        "doc/", "docs/", "wiki/", "manual/", "guide/",
        "src/", "source/", "lib/", "library/", "modules/",
        "plugins/", "components/", "templates/", "themes/", "layouts/",
        "configs/", "settings/", "profiles/", "accounts/", "groups/",
        "permissions/", "roles/", "policies/", "rules/", "triggers/",
        "events/", "listeners/", "subscribers/", "observers/", "handlers/",
        "commands/", "controllers/", "models/", "views/", "routes/",
        "middleware/", "providers/", "factories/", "migrations/", "seeds/",
        "fixtures/", "schemas/", "entities/", "repositories/", "services/",
        "interfaces/", "abstracts/", "traits/", "helpers/", "utilities/",
        "validators/", "transformers/", "serializers/", "parsers/", "generators/",
        "caches/", "sessions/", "cookies/", "tokens/", "keys/",
        "certificates/", "credentials/", "secrets/", "passwords/", "hashes/",
    ]

def probar_directorio(url_base, directorio, headers, encontrados, f, lineas):
    """Prueba un directorio"""
    url = f"{url_base}/{directorio}"
    try:
        r = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
        if r.status_code in [200, 301, 302, 403]:
            if r.status_code == 200:
                color = V
                icono = "✓"
            elif r.status_code in [301, 302]:
                color = A
                icono = "→"
            else:
                color = R
                icono = "⊘"
            
            print(f"  {color}[{r.status_code}] {icono} {url}{N}")
            f.write(f"[{r.status_code}] {url}\n")
            encontrados.append({"url": url, "status": r.status_code, "size": len(r.content)})
        elif r.status_code == 401:
            print(f"  {A}[401] 🔒 {url}{N}")
            f.write(f"[401] {url}\n")
            encontrados.append({"url": url, "status": 401})
        elif r.status_code == 500:
            print(f"  {R}[500] ⚠ {url}{N}")
            f.write(f"[500] {url}\n")
            encontrados.append({"url": url, "status": 500})
    except:
        pass

def main():
    banner()
    
    url = input(f"{B}URL objetivo:{N} ").strip()
    if not url.startswith("http"):
        url = "http://" + url
    url = url.rstrip("/")
    
    print(f"\n{B}[*] Información del objetivo{N}\n")
    headers = {"User-Agent": "DirectoryBruteForcer/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"  URL: {url}")
        print(f"  Servidor: {r.headers.get('Server', 'Desconocido')}")
        print(f"  Status: {r.status_code}")
        print(f"  Tamaño: {len(r.content)} bytes\n")
    except:
        print(f"  {R}[!] No se pudo conectar{N}\n")
        return
    
    # Hilos
    try:
        hilos = int(input(f"{B}Hilos (1-10, Enter=4):{N} ") or "4")
        hilos = max(1, min(10, hilos))
    except:
        hilos = 4
    
    # Wordlist
    wordlist = cargar_wordlist(url)
    print(f"\n[*] Wordlist cargada: {len(wordlist)} directorios")
    print(f"[*] Hilos: {hilos}")
    print(f"[*] Tiempo estimado: ~{len(wordlist)//hilos//2} segundos\n")
    
    input(f"{B}Presiona Enter para empezar...{N}")
    
    encontrados = []
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"dirscan_{url.replace('://', '_').replace('/', '_')[:30]}_{ts}.txt"
    
    print(f"\n{B}[*] Escaneando...{N}\n")
    
    with open(nombre_archivo, "w") as f:
        f.write(f"Directory Brute Forcer\n")
        f.write(f"Objetivo: {url}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Wordlist: {len(wordlist)} directorios\n")
        f.write(f"{'='*50}\n\n")
        
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=hilos) as executor:
            for directorio in wordlist:
                executor.submit(probar_directorio, url, directorio, headers, encontrados, f, 0)
        
        f.write(f"\n{'='*50}\n")
        f.write(f"Total: {len(encontrados)} directorios encontrados\n")
    
    print(f"\n{C}{B}{'='*50}{N}")
    print(f"{C}{B}   RESULTADOS{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Directorios encontrados: {V}{len(encontrados)}{N}")
    print(f"  Archivo: {nombre_archivo}")
    print(f"{C}{'='*50}{N}\n")
    
    if encontrados:
        for i, d in enumerate(encontrados, 1):
            if d['status'] == 200:
                print(f"  {V}{i}. [{d['status']}] {d['url']} ({d['size']} bytes){N}")
            elif d['status'] in [301, 302]:
                print(f"  {A}{i}. [{d['status']}] {d['url']}{N}")
            else:
                print(f"  {R}{i}. [{d['status']}] {d['url']}{N}")
    
    os.system("pause")

if __name__ == "__main__":
    main()
