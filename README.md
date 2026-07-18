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

### 3. Validación Social (`src/filters_ig.py`)
Módulo crítico que evade el bloqueo de login de Instagram. 
- Utiliza la técnica de *OpenGraph Spoofing* inyectando un `User-Agent` de Discordbot. 
- Extrae pasivamente la etiqueta `<meta property="og:description">` para parsear la métrica de seguidores mediante expresiones regulares.
- Implementa la función lógica de filtrado comercial (1,500 a 5,000 seguidores), priorizando cuentas con volumen suficiente para invertir, pero sin infraestructura in-house.

### 4. Orquestación y Exportación (`main.py` y `src/exporter.py`)
El archivo `main.py` controla el flujo asíncrono-síncrono. Pasa la matriz de leads crudos por los filtros de enriquecimiento y delega la serialización a `exporter.py`, el cual utiliza `pandas` para generar un CSV estructurado y ordenado por prioridad comercial.

## Ejecución del Sistema

Para ejecutar el pipeline completo, define tu query de búsqueda dentro del bloque `__main__` en `main.py` y ejecuta:

```bash
python main.py


