# Proxy Finder

Alat Python untuk menemukan proxy HTTP, HTTPS, dan SOCKS5 yang aktif dengan dukungan WebSocket, lalu menyimpannya secara rapi ke file teks.

## Fitur Utama

- ✅ Pemeriksaan proxy untuk protokol HTTP, HTTPS, dan SOCKS5
- ✅ Verifikasi dukungan WebSocket
- ✅ Pemeriksaan multi-threading untuk kinerja cepat
- ✅ Penyimpanan otomatis ke file `proxies.txt`
- ✅ Format penyimpanan yang konsisten (`http://`, `https://`, `socks5://`)
- ✅ Progress reporting real-time
- ✅ Dukungan proxy dalam format `ip:port` atau `domain:port`

## Persyaratan

- Python 3.6+
- Dependencies:
  ```bash
  pip install requests websocket-client
  ```

## Cara Menggunakan

1. Clone repositori:
   ```bash
   git clone https://github.com/dicoderin/proxyfind.git
   cd proxyfind
   ```

2. Buat file `input.txt` yang berisi daftar proxy (format: `ip:port` atau `domain:port`):
   ```
   123.45.67.89:8080
   proxy.example.com:3128
   111.222.333.444:1080
   ```

3. Jalankan script:
   ```bash
   python find.py
   ```

4. Hasil akan disimpan di `proxies.txt`:
   ```
   http://123.45.67.89:8080
   https://proxy.example.com:3128
   socks5://111.222.333.444:1080
   ```

## Output Contoh

```
Mulai mengecek 150 proxy...
✅ Ditemukan 1 proxy valid | 1/150
❌ Tidak valid | 2/150
✅ Ditemukan 2 proxy valid | 3/150
...

Selesai! 23 proxy valid ditemukan
Durasi: 120.45 detik
Hasil disimpan di proxies.txt
```

## Struktur File

- `proxy_checker.py` - Skrip utama
- `input.txt` - Input proxy (dibuat pengguna)
- `proxies.txt` - Output proxy valid (dihasilkan otomatis)
- `README.md` - Dokumentasi ini

## Metode Pemeriksaan

1. **Pemeriksaan HTTP/HTTPS**:
   - Menggunakan [httpbin.org/ip](https://httpbin.org/ip)
   - Memverifikasi respons 200 OK
   - Timeout: 10 detik

2. **Pemeriksaan WebSocket**:
   - Menggunakan [wss://echo.websocket.org](wss://echo.websocket.org)
   - Mengirim pesan "PING" dan memverifikasi respons
   - Mendukung proxy HTTP dan SOCKS5

3. **Kinerja**:
   - Multi-threading (20 worker)
   - Pemeriksaan paralel
   - Penanganan kesalahan otomatis

## Kontribusi

Kontribusi diterima! Silakan ajukan:
1. Issue untuk melaporkan bug atau meminta fitur
2. Pull request dengan perbaikan atau peningkatan

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

**Disclaimer**: Gunakan alat ini hanya untuk tujuan legal. Penulis tidak bertanggung jawab atas penyalahgunaan proxy yang ditemukan.
