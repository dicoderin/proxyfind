import requests
from websocket import create_connection, WebSocketConnectionClosedException
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def test_http_proxy(proxy_type, proxy_url):
    """Test proxy untuk koneksi HTTP/HTTPS"""
    proxies = {
        'http': f'{proxy_type}://{proxy_url}',
        'https': f'{proxy_type}://{proxy_url}'
    }
    try:
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def test_websocket_proxy(proxy_type, proxy_url):
    """Test proxy untuk koneksi WebSocket"""
    try:
        if proxy_type == 'socks5':
            ws = create_connection(
                "wss://echo.websocket.org",
                sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                http_proxy_host=proxy_url.split(':')[0],
                http_proxy_port=int(proxy_url.split(':')[1]),
                proxy_type='socks5'
            )
        else:
            ws = create_connection(
                "wss://echo.websocket.org",
                sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                http_proxy_host=proxy_url.split(':')[0],
                http_proxy_port=int(proxy_url.split(':')[1])
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
    
    # Gunakan multithreading untuk mempercepat proses
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        
        for future in as_completed(future_to_proxy):
            checked += 1
            result = future.result()
            if result:
                valid_proxies.extend(result)
                print(f"✅ Ditemukan {len(result)} proxy valid | {checked}/{total_proxies}")
            else:
                print(f"❌ Tidak valid | {checked}/{total_proxies}")
    
    # Simpan proxy yang valid
    with open('proxies.txt', 'w') as f:
        for proxy in valid_proxies:
            f.write(proxy + '\n')
    
    duration = time.time() - start_time
    print(f"\nSelesai! {len(valid_proxies)} proxy valid ditemukan")
    print(f"Durasi: {duration:.2f} detik")
    print(f"Hasil disimpan di proxies.txt")

if __name__ == "__main__":
    import socket
    main()
