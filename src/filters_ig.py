import requests
from bs4 import BeautifulSoup
import re
import time

def parse_followers(follower_str: str) -> int:
    """Convierte métricas en cadena ('1.5M', '10.2K', '1,500') a números enteros."""
    clean_str = follower_str.replace(',', '').upper()
    try:
        if 'K' in clean_str:
            return int(float(clean_str.replace('K', '')) * 1000)
        elif 'M' in clean_str:
            return int(float(clean_str.replace('M', '')) * 1000000)
        else:
            return int(clean_str)
    except ValueError:
        return 0

def get_instagram_followers(ig_url: str) -> int | None:
    """Extrae seguidores utilizando un visor de terceros (Picuki) como puente OSINT."""
    if not ig_url:
        return None
        
    username = ig_url.rstrip('/').split('?')[0].split('/')[-1]
    if not username:
        return None

    url = f"https://www.picuki.com/profile/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    try:
        time.sleep(1) # Respetar rate-limit del puente
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Búsqueda dinámica del nodo de seguidores en el DOM de Picuki
        for element in soup.find_all(['li', 'div', 'span']):
            text = element.get_text(strip=True).lower()
            if 'follower' in text or 'seguidor' in text:
                match = re.search(r'([\d\.,km]+)\s*(?:followers?|seguidores?)', text)
                if match:
                    return parse_followers(match.group(1))
                    
        return None
    except requests.RequestException:
        return None

def is_target_lead(followers: int, min_f: int = 1500, max_f: int = 5000) -> bool:
    """Valida si la cuenta cae en el 'punto dulce' comercial."""
    if followers is None:
        return False
    return min_f <= followers <= max_f

if __name__ == "__main__":
    test_profiles = [
        "https://www.instagram.com/nike",       
        "https://www.instagram.com/github",     
        "https://www.instagram.com/nonexistent_profile_123456" 
    ]
    
    print("Iniciando validación de métricas (Proxy Picuki)...\n")
    for profile in test_profiles:
        followers = get_instagram_followers(profile)
        is_target = is_target_lead(followers)
        print(f"Perfil: {profile}")
        print(f"Seguidores: {followers} | Objetivo comercial: {is_target}\n")
        