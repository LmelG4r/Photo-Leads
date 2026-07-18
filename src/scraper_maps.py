import asyncio
from playwright.async_api import async_playwright, Page

async def extract_place_metadata(page: Page, url: str) -> dict:
    """Visita la URL de un negocio específico, espera la carga dinámica y extrae metadatos."""
    await page.goto(url)
    
    # Barrera de sincronización: Esperar inyección JS del panel principal
    try:
        await page.wait_for_selector('h1', timeout=8000, state="visible")
    except Exception:
        return {"name": None, "website": None, "phone": None, "maps_url": url}
    
    name_loc = page.locator('h1').first
    name = await name_loc.inner_text() if await name_loc.count() > 0 else None
    
    # Selectores web con fallback (authority ID o aria-label)
    website_loc = page.locator('a[data-item-id="authority"], a[aria-label*="Sitio web"]').first
    website = await website_loc.get_attribute('href') if await website_loc.count() > 0 else None
    
    # Selectores de teléfono con extracción desde aria-label o ID
    phone_loc = page.locator('button[data-item-id*="phone"], button[aria-label*="Teléfono"]').first
    phone = None
    if await phone_loc.count() > 0:
        aria_label = await phone_loc.get_attribute('aria-label')
        if aria_label and ":" in aria_label:
            # Formato esperado: "Teléfono: 55 1234 5678"
            phone = aria_label.split(":")[-1].strip()
        else:
            raw_phone = await phone_loc.get_attribute('data-item-id')
            if raw_phone:
                phone = raw_phone.replace('phone:numeric', '').replace('phone:', '').strip()
            
    return {
        "name": name,
        "website": website,
        "phone": phone,
        "maps_url": url
    }

async def scrape_google_maps(search_query: str, max_results: int = 10) -> list[dict]:
    """Orquesta la búsqueda, recolección de enlaces y extracción de datos."""
    leads = []
    
    async with async_playwright() as p:
        # Modo headless activado para mayor velocidad en entorno de producción
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="es-ES")
        page = await context.new_page()
        
        formatted_query = search_query.replace(' ', '+')
        search_url = f"https://www.google.com/maps/search/{formatted_query}"
        
        await page.goto(search_url)
        
        try:
            await page.wait_for_selector('div[role="feed"]', timeout=10000)
        except Exception:
            print("Error: No se encontró el contenedor de resultados. Posible redirección directa a un único resultado.")
            await browser.close()
            return leads
            
        urls = set()
        feed_selector = 'div[role="feed"]'
        
        # Pasada 1: Recolección de URLs con scroll dinámico
        while len(urls) < max_results:
            links = await page.locator('a[href*="/maps/place/"]').element_handles()
            
            for link in links:
                href = await link.get_attribute('href')
                if href and href not in urls:
                    urls.add(href)
                    
            if len(urls) >= max_results:
                break
                
            # Ejecución JS para forzar el scroll del contenedor interno
            await page.evaluate(f'''
                const feed = document.querySelector('{feed_selector}');
                if(feed) feed.scrollBy(0, 1500);
            ''')
            await page.wait_for_timeout(2000) # Espera para renderizado de la red
            
        urls_list = list(urls)[:max_results]
        
        # Pasada 2: Extracción de metadatos por URL
        for url in urls_list:
            try:
                data = await extract_place_metadata(page, url)
                leads.append(data)
            except Exception as e:
                # El manejo de errores aísla el fallo de un nodo para no detener el batch
                continue
                
        await browser.close()
        
    return leads

if __name__ == "__main__":
    # Bloque de prueba de ejecución aislada
    query = "restaurantes en Ciudad Nicolás Romero"
    print(f"Iniciando extracción de prueba para: '{query}'")
    
    results = asyncio.run(scrape_google_maps(query, max_results=3))
    
    for idx, r in enumerate(results, 1):
        print(f"\nLead {idx}:")
        print(f"Nombre: {r['name']}")
        print(f"Web: {r['website']}")
        print(f"Teléfono: {r['phone']}")