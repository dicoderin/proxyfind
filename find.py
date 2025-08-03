import asyncio
import aiohttp
import socket
import random
import time
import json
import os
from aiohttp_socks import ProxyConnector
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
import aiodns
import maxminddb
from datetime import datetime
import logging

# Konfigurasi
CONFIG = {
    "input_file": "input.txt",
    "output_file": "proxies.txt",
    "json_file": "proxies.json",
    "timeout": 15,
    "max_concurrent": 200,
    "test_sites": {
        "http": [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://www.bing.com",
            "https://www.github.com"
        ],
        "websocket": [
            "wss://echo.websocket.org",
            "wss://ws.postman-echo.com/raw",
            "wss://socketsbay.com/wss/v2/1/demo/"
        ]
    },
    "geolite_path": "GeoLite2-Country.mmdb"  # Unduh dari: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("proxy_checker.log"),
        logging.StreamHandler()
    ]
)

console = Console()

class ProxyChecker:
    def __init__(self):
        self.valid_proxies = []
        self.stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "start_time": time.time(),
            "by_protocol": {"http": 0, "https": 0, "socks5": 0},
            "by_country": {}
        }
        self.geoip_reader = None
        self.dns_resolver = aiodns.DNSResolver()
        
        # Load GeoIP database if available
        if os.path.exists(CONFIG["geolite_path"]):
            try:
                self.geoip_reader = maxminddb.open_database(CONFIG["geolite_path"])
                logging.info("GeoIP database loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load GeoIP database: {e}")
    
    async def resolve_host(self, host):
        """Resolve host to IP address asynchronously"""
        try:
            result = await self.dns_resolver.gethostbyname(host, socket.AF_INET)
            return result.addresses[0] if result.addresses else host
        except:
            return host
    
    async def get_location(self, ip):
        """Get country for IP using GeoIP database"""
        if not self.geoip_reader:
            return "Unknown"
        
        try:
            response = self.geoip_reader.get(ip)
            return response.get('country', {}).get('names', {}).get('en', 'Unknown')
        except:
            return "Unknown"
    
    async def test_http(self, session, proxy_type, proxy_url):
        """Test HTTP/HTTPS proxy with multiple targets"""
        test_url = random.choice(CONFIG["test_sites"]["http"])
        try:
            async with session.get(test_url, timeout=CONFIG["timeout"]) as response:
                if response.status == 200:
                    return True
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
        return False
    
    async def test_websocket(self, proxy_type, proxy_url):
        """Test WebSocket connection through proxy"""
        test_url = random.choice(CONFIG["test_sites"]["websocket"])
        test_message = f"TEST-{random.randint(1000, 9999)}"
        
        connector = None
        if proxy_type == "socks5":
            connector = ProxyConnector.from_url(f"socks5://{proxy_url}")
        else:
            connector = ProxyConnector.from_url(f"{proxy_type}://{proxy_url}")
        
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.ws_connect(
                    test_url, 
                    timeout=CONFIG["timeout"],
                    heartbeat=10
                ) as ws:
                    await ws.send_str(test_message)
                    response = await ws.receive_str(timeout=10)
                    if response == test_message:
                        return True
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
        return False
    
    async def check_proxy(self, proxy_line):
        """Check proxy for all protocols and features"""
        proxy_line = proxy_line.strip()
        if not proxy_line:
            return None
        
        # Extract IP and port
        proxy_parts = proxy_line.split(":")
        if len(proxy_parts) < 2:
            return None
        
        ip = await self.resolve_host(proxy_parts[0])
        port = proxy_parts[1]
        country = await self.get_location(ip)
        
        valid_results = []
        
        # Test each protocol
        for protocol in ["http", "https", "socks5"]:
            try:
                # Skip WebSocket test for HTTPS proxies
                skip_ws = (protocol == "https")
                
                # Test HTTP connectivity
                connector = ProxyConnector.from_url(f"{protocol}://{proxy_line}")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
                
                async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                    http_ok = await self.test_http(session, protocol, proxy_line)
                    
                    if http_ok:
                        # Test WebSocket if applicable
                        ws_ok = skip_ws or await self.test_websocket(protocol, proxy_line)
                        
                        if ws_ok:
                            result = {
                                "protocol": protocol,
                                "proxy": proxy_line,
                                "url": f"{protocol}://{proxy_line}",
                                "ip": ip,
                                "port": port,
                                "country": country,
                                "validated_at": datetime.utcnow().isoformat()
                            }
                            valid_results.append(result)
                            self.stats["by_protocol"][protocol] += 1
            except Exception as e:
                logging.debug(f"Error testing {protocol}://{proxy_line}: {e}")
        
        # Update country stats
        if valid_results:
            self.stats["by_country"][country] = self.stats["by_country"].get(country, 0) + 1
        
        return valid_results
    
    def save_results(self):
        """Save results to files"""
        # Save to text file
        with open(CONFIG["output_file"], "w") as f:
            for proxy in self.valid_proxies:
                f.write(proxy["url"] + "\n")
        
        # Save to JSON file
        with open(CONFIG["json_file"], "w") as f:
            json.dump(self.valid_proxies, f, indent=2)
        
        # Save stats
        with open("stats.json", "w") as f:
            json.dump(self.stats, f, indent=2)
    
    def print_stats(self):
        """Print statistics to console"""
        duration = time.time() - self.stats["start_time"]
        table = Table(title="Proxy Checker Statistics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Total Proxies", str(self.stats["total"]))
        table.add_row("Valid Proxies", str(self.stats["valid"]))
        table.add_row("Invalid Proxies", str(self.stats["invalid"]))
        table.add_row("Duration", f"{duration:.2f} seconds")
        table.add_row("Speed", f"{self.stats['total']/max(duration, 1):.2f} proxies/sec")
        
        # Protocol distribution
        for protocol, count in self.stats["by_protocol"].items():
            table.add_row(f"{protocol.upper()} Proxies", str(count))
        
        # Top countries
        sorted_countries = sorted(self.stats["by_country"].items(), key=lambda x: x[1], reverse=True)[:5]
        for country, count in sorted_countries:
            table.add_row(f"Top Country: {country}", str(count))
        
        console.print(table)

async def main():
    # Load proxies
    if not os.path.exists(CONFIG["input_file"]):
        logging.error(f"Input file {CONFIG['input_file']} not found!")
        return
    
    with open(CONFIG["input_file"], "r") as f:
        proxies = f.readlines()
    
    if not proxies:
        logging.warning("No proxies found in input file")
        return
    
    checker = ProxyChecker()
    checker.stats["total"] = len(proxies)
    
    logging.info(f"Starting proxy check for {len(proxies)} proxies...")
    
    # Setup progress bar
    with Progress(transient=True) as progress:
        task = progress.add_task("[cyan]Checking proxies...", total=len(proxies))
        
        # Process proxies in batches
        batch_size = CONFIG["max_concurrent"]
        for i in range(0, len(proxies), batch_size):
            batch = proxies[i:i + batch_size]
            tasks = [checker.check_proxy(p) for p in batch]
            
            for future in asyncio.as_completed(tasks):
                results = await future
                progress.update(task, advance=1)
                
                if results:
                    checker.valid_proxies.extend(results)
                    checker.stats["valid"] += len(results)
                    for result in results:
                        logging.info(f"✅ Valid: {result['protocol']}://{result['proxy']} ({result['country']})")
                else:
                    checker.stats["invalid"] += 1
    
    # Save results
    checker.save_results()
    checker.print_stats()
    
    logging.info(f"\nCompleted! {checker.stats['valid']} valid proxies found")
    logging.info(f"Results saved to {CONFIG['output_file']} and {CONFIG['json_file']}")

if __name__ == "__main__":
    asyncio.run(main())
