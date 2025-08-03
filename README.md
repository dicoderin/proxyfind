# Proxy Finder Modern

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![GitHub Stars](https://img.shields.io/github/stars/dicoderin/proxyfind.svg)](https://github.com/dicoderin/proxyfind/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/dicoderin/proxyfind.svg)](https://github.com/dicoderin/proxyfind/issues)

Alat canggih untuk menemukan proxy HTTP, HTTPS, dan SOCKS5 yang aktif dengan dukungan WebSocket. Dibangun dengan teknologi modern Python dan arsitektur asinkron untuk performa tinggi.

## ✨ Fitur Unggulan

- **Multi-Protocol Support** - Mendukung HTTP, HTTPS, dan SOCKS5
- **WebSocket Validation** - Pemeriksaan dukungan WebSocket yang akurat
- **Geolocation Tracking** - Deteksi negara asal proxy
- **High Performance** - Pemeriksaan hingga 200 proxy secara bersamaan
- **Rich Reporting** - Statistik visual dan output multi-format
- **Advanced Testing** - Multi-endpoint testing dengan payload unik
- **Smart DNS** - Resolusi DNS asinkron dengan caching

## 📦 Instalasi

1. Clone repositori:
```bash
git clone https://github.com/dicoderin/proxyfind.git
cd proxyfind
```

2. Install dependencies:
```bash
pip install aiohttp aiohttp_socks rich aiodns maxminddb
```

3. Download GeoLite2 database (gratis):
- Daftar di [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- Tempatkan file `GeoLite2-Country.mmdb` di folder utama

## 🚀 Penggunaan

1. Siapkan file input (`input.txt`) dengan daftar proxy (format: `ip:port` atau `domain:port`):
```
123.45.67.89:8080
proxy.example.com:3128
111.222.333.444:1080
```

2. Jalankan checker:
```bash
python find.py
```

3. Lihat hasil di:
- `proxies.txt` - Proxies valid format teks
- `proxies.json` - Proxies valid dengan metadata lengkap
- `stats.json` - Statistik pengecekan

## ⚙️ Konfigurasi

Edit bagian `CONFIG` di `find.py` untuk penyesuaian:

```python
CONFIG = {
    "input_file": "input.txt",          # File input
    "output_file": "proxies.txt",       # Output teks
    "json_file": "proxies.json",        # Output JSON
    "timeout": 15,                      # Timeout koneksi (detik)
    "max_concurrent": 200,              # Jumlah maksimal proxy bersamaan
    "test_sites": {                     # Daftar endpoint testing
        "http": [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://www.bing.com"
        ],
        "websocket": [
            "wss://echo.websocket.org",
            "wss://ws.postman-echo.com/raw"
        ]
    },
    "geolite_path": "GeoLite2-Country.mmdb"  # Path database GeoIP
}
```

## 📂 Struktur File

```
proxyfind/
├── find.py       # Skrip utama
├── input.txt              # Input proxy (dibuat pengguna)
├── proxies.txt            # Output proxy valid
├── proxies.json           # Output JSON dengan metadata
├── stats.json             # Statistik pengecekan
├── proxy_checker.log      # Log file
├── GeoLite2-Country.mmdb  # Database GeoIP (unduh terpisah)
├── requirements.txt       # Dependencies
├── README.md              # Dokumentasi ini
└── LICENSE                # Lisensi MIT
```

## 🧪 Metode Pemeriksaan

1. **HTTP/HTTPS Test**:
   - Mengirim request ke berbagai situs populer
   - Memverifikasi respons 200 OK
   - Timeout konfigurasi

2. **WebSocket Test**:
   - Membuat koneksi WebSocket nyata
   - Mengirim payload unik dan memverifikasi respons
   - Mendukung protokol SOCKS5 dan HTTP

3. **Geolocation**:
   - Resolusi IP asinkron
   - Deteksi negara menggunakan database GeoLite2
   - Statistik berdasarkan negara

4. **Performance**:
   - Arsitektur asinkron berbasis asyncio
   - Connection pooling
   - Batch processing

## 🤝 Kontribusi

Kontribusi diterima! Ikuti langkah:
1. Fork repository
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Tambahkan fitur'`)
4. Push branch (`git push origin fitur-baru`)
5. Buat Pull Request

Atau laporkan bug melalui [issues](https://github.com/dicoderin/proxyfind/issues).

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

**Disclaimer**: Gunakan alat ini hanya untuk tujuan legal. Pengembang tidak bertanggung jawab atas penyalahgunaan proxy yang ditemukan.
