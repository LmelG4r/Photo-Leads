# LeadLens-Photo

Sistema de automatización en Python para la extracción, validación y filtrado de leads comerciales locales. Diseñado específicamente para identificar negocios de comida con tracción social (1,500 - 5,000 seguidores en Instagram) que requieran servicios de fotografía profesional.

## Arquitectura

El sistema opera bajo un flujo de 4 etapas desacopladas:
1. **Scraping Local:** Extracción de negocios vía Google Maps (`src/scraper_maps.py`).
2. **Extracción Web:** Búsqueda de metadatos y enlaces sociales (`src/extraction_web.py`).
3. **Validación Social:** Lectura asíncrona y ligera de métricas de Instagram (`src/filters_ig.py`).
4. **Exportación:** Procesamiento de la matriz de datos hacia CSV (`src/exporter.py`).

## Instalación y Despliegue

Requiere Python 3.10+.

1. Clonar el repositorio y acceder al directorio.
2. Crear y activar el entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate

## Uso de Módulos Independientes

### 1. Scraper de Google Maps (`src/scraper_maps.py`)
Utiliza Playwright asíncrono para evadir restricciones básicas. Opera mediante una estrategia de "Two-Pass":
1. Scroll vertical en el DOM para resolver peticiones AJAX y capturar URLs únicas de lugares.
2. Navegación iterativa hacia cada URL recolectada para extraer los selectores definitivos (`h1`, `a[data-item-id="authority"]`, `button[data-item-id^="phone"]`).

**Limitaciones conocidas:** Los selectores DOM de Google cambian periódicamente. Si la extracción devuelve `None` en los campos `website` o `phone`, es necesario inspeccionar la estructura web actual de Maps y actualizar los selectores en la función `extract_place_metadata`.

### 2. Extracción Web y Metadatos (`src/extraction_web.py`)
Módulo de escaneo estático basado en `requests` y `BeautifulSoup`. Opera bajo una lógica de bajo consumo computacional.
- Valida si la URL de origen ya es un perfil de Instagram.
- Ejecuta peticiones HTTP con un timeout restrictivo (8 segundos) para evitar bloqueos por dominios inactivos.
- Filtra rutas inválidas (`/p/`, `/reel/`) mediante la función `clean_instagram_url` para asegurar que el dato exportado es un perfil prospeccionable.

