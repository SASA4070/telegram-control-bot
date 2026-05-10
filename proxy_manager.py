import requests
import random
import os
from config import USE_PROXY, PROXY_FILE  # <-- أضف هذا السطر

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.load_proxies()
    
    def load_proxies(self):
        """تحميل البروكسيات من الملف"""
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        
        if not self.proxies:
            self.fetch_free_proxies()
    
    def fetch_free_proxies(self):
        """جلب بروكسيات مجانية من API"""
        try:
            response = requests.get(
                'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all',
                timeout=10
            )
            if response.status_code == 200:
                self.proxies = [p.strip() for p in response.text.split('\r\n') if p.strip()]
            
            if len(self.proxies) < 10:
                response = requests.get('https://free-proxy-list.net/', timeout=10)
                import re
                found = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)<tr><td>(\d+)<table>', response.text)
                self.proxies = [f"{ip}:{port}" for ip, port in found[:50]]
        
        except Exception as e:
            print(f"Proxy fetch error: {e}")
        
        if not self.proxies:
            self.proxies = [
                "104.238.110.154:8080",
                "192.252.220.117:80",
                "50.221.230.166:80",
                "66.29.128.242:80",
                "103.169.142.224:80",
            ]
    
    def get_proxy(self):
        """جلب بروكسي عشوائي"""
        if not USE_PROXY or not self.proxies:
            return None
        return {"http": f"http://{random.choice(self.proxies)}", "https": f"http://{random.choice(self.proxies)}"}
    
    def rotate_proxy(self):
        """تغيير البروكسي"""
        self.current_index = (self.current_index + 1) % len(self.proxies) if self.proxies else 0
        return self.get_proxy()

proxy_manager = ProxyManager()