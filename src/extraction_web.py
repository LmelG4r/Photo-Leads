import requests
from bs4 import BeautifulSoup

def clean_instagram_url(url: str) -> str | None:
    """Limpia la URL y valida que corresponda a un perfil, no a una publicación ni a la raíz."""
    if not url:
        return None
    
    clean_url = url.split('?')[0].rstrip('/')
    
    invalid_paths = ['/p/', '/reel/', '/explore/', '/stories/', '/tags/', '/developer/']
    if any(path in clean_url for path in invalid_paths):
        return None
        
    # Filtrar enlaces genéricos a la página principal de Instagram
    generic_urls = ["https://instagram.com", "https://www.instagram.com", "http://instagram.com", "http://www.instagram.com"]
    if clean_url in generic_urls:
        return None
        
    return clean_url if "instagram.com" in clean_url else None

def extract_instagram_from_website(website_url: str) -> str | None:
    """Realiza una petición HTTP GET al sitio web y extrae el primer enlace válido a Instagram."""
    if not website_url:
        return None
        
    # Si Google Maps ya proporcionó directamente el enlace de Instagram como sitio web
    if "instagram.com" in website_url:
        return clean_instagram_url(website_url)
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(website_url, headers=headers, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        # Falla silenciosa para evitar detener el batch por un dominio caído o firewall restrictivo
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Búsqueda de nodos ancla con referencia a Instagram
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "instagram.com" in href:
            valid_url = clean_instagram_url(href)
            if valid_url:
                return valid_url
                
    return None

if __name__ == "__main__":
    # Bloque de prueba aislada
    test_urls = [
        "https://santasalitas.com/",                  # Web estándar (debería tener redes)
        "https://www.facebook.com/Tmunchies420/",     # Enlace de Facebook
        None                                          # Sin sitio web
    ]
    
    print("Iniciando escaneo social de prueba...\n")
    for url in test_urls:
        ig_url = extract_instagram_from_website(url)
        print(f"URL Origen: {url}")
        print(f"Instagram: {ig_url}\n")