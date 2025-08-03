import requests
import socket
from websocket import create_connection, WebSocketConnectionClosedException
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

# Daftar User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Daftar target HTTP untuk pengecekan
HTTP_TARGETS = [
    "https://httpbin.org/ip",
    "https://api.ipify.org?format=json",
    "https://ipinfo.io/json"
]

def test_http_proxy(proxy_type, proxy_url):
    """Test proxy untuk koneksi HTTP/HTTPS"""
    proxies = {
        'http': f'{proxy_type}://{proxy_url}',
        'https': f'{proxy_type}://{proxy_url}'
    }
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    for target in HTTP_TARGETS:
        try:
            response = requests.get(
                target,
                headers=headers,
                proxies=proxies,
                timeout=20
            )
            if response.status_code == 200:
                return True
        except:
            continue
    return False

def test_websocket_proxy(proxy_type, proxy_url):
    """Test proxy untuk koneksi WebSocket"""
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        if proxy_type == 'socks5':
            ws = create_connection(
                "wss://echo.websocket.org",
                sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                http_proxy_host=proxy_url.split(':')[0],
                http_proxy_port=int(proxy_url.split(':')[1]),
                proxy_type='socks5',
                header=headers,
                timeout=20
            )
        else:
            ws = create_connection(
                "wss://echo.websocket.org",
                sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                http_proxy_host=proxy_url.split(':')[0],
                http_proxy_port=int(proxy_url.split(':')[1]),
                header=headers,
                timeout=20
            )
        
        ws.send("PING")
        response = ws.recv()
        ws.close()
        return response == "PING"
    except:
        return False

def check_proxy(proxy):
    """Cek proxy untuk semua protokol dan WebSocket"""
    proxy = proxy.strip()
    if not proxy:
        return None

    valid_proxies = []
    
    # Cek tipe proxy
    for proxy_type in ['http', 'https', 'socks5']:
        try:
            # Test koneksi dasar
            if test_http_proxy(proxy_type, proxy):
                # Test WebSocket khusus untuk protokol yang relevan
                if proxy_type in ['http', 'socks5']:
                    if test_websocket_proxy(proxy_type, proxy):
                        valid_proxies.append(f"{proxy_type}://{proxy}")
                else:  # Untuk HTTPS proxy
                    valid_proxies.append(f"{proxy_type}://{proxy}")
        except:
            continue
    
    return valid_proxies

def main():
    # Baca proxy dari file input
    with open('input.txt', 'r') as f:
        proxies = f.readlines()
    
    valid_proxies = []
    total_proxies = len(proxies)
    checked = 0
    
    print(f"Mulai mengecek {total_proxies} proxy...")
    start_time = time.time()
    
    # Gunakan multithreading untuk mempercepat proses, kurangi worker jika diperlukan
    max_workers = min(20, total_proxies)  # Maksimal 20 worker
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        
        for future in as_completed(future_to_proxy):
            checked += 1
            result = future.result()
            proxy_checked = future_to_proxy[future].strip()
            if result:
                valid_proxies.extend(result)
                print(f"✅ Ditemukan {len(result)} proxy valid untuk {proxy_checked} | {checked}/{total_proxies}")
            else:
                print(f"❌ Tidak valid: {proxy_checked} | {checked}/{total_proxies}")
    
    # Simpan proxy yang valid
    with open('proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')
    
    duration = time.time() - start_time
    print(f"\nSelesai! {len(valid_proxies)} proxy valid ditemukan")
    print(f"Durasi: {duration:.2f} detik")
    print(f"Hasil disimpan di proxies.txt")

if __name__ == "__main__":
    main()
